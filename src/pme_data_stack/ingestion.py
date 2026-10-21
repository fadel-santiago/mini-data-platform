from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from psycopg import Connection, sql

from .config import Settings
from .db import connect, initialise_schemas


Converter = Callable[[str], Any]


def as_int(value: str) -> int:
    return int(value)


def as_decimal(value: str) -> str:
    return value


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "oui"}


def as_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class SourceSpec:
    name: str
    filename: str
    table: str
    primary_key: tuple[str, ...]
    columns: dict[str, str]
    converters: dict[str, Converter]
    watermark_column: str = "updated_at"


SOURCES = (
    SourceSpec(
        name="crm_customers",
        filename="crm_customers.csv",
        table="customers",
        primary_key=("customer_id",),
        columns={
            "customer_id": "text",
            "company_name": "text",
            "segment": "text",
            "region": "text",
            "created_at": "date",
            "updated_at": "timestamptz",
        },
        converters={"updated_at": as_timestamp},
    ),
    SourceSpec(
        name="crm_orders",
        filename="crm_orders.csv",
        table="orders",
        primary_key=("order_id",),
        columns={
            "order_id": "text",
            "customer_id": "text",
            "order_date": "date",
            "status": "text",
            "channel": "text",
            "updated_at": "timestamptz",
        },
        converters={"updated_at": as_timestamp},
    ),
    SourceSpec(
        name="erp_order_lines",
        filename="erp_order_lines.csv",
        table="order_lines",
        primary_key=("order_id", "line_id"),
        columns={
            "order_id": "text",
            "line_id": "integer",
            "product_id": "text",
            "quantity": "integer",
            "unit_price": "numeric(14,2)",
            "unit_cost": "numeric(14,2)",
            "updated_at": "timestamptz",
        },
        converters={
            "line_id": as_int,
            "quantity": as_int,
            "unit_price": as_decimal,
            "unit_cost": as_decimal,
            "updated_at": as_timestamp,
        },
    ),
    SourceSpec(
        name="erp_inventory",
        filename="erp_inventory.csv",
        table="inventory",
        primary_key=("product_id",),
        columns={
            "product_id": "text",
            "product_name": "text",
            "category": "text",
            "stock_quantity": "integer",
            "reorder_point": "integer",
            "unit_cost": "numeric(14,2)",
            "updated_at": "timestamptz",
        },
        converters={
            "stock_quantity": as_int,
            "reorder_point": as_int,
            "unit_cost": as_decimal,
            "updated_at": as_timestamp,
        },
    ),
    SourceSpec(
        name="finance_invoices",
        filename="finance_invoices.csv",
        table="invoices",
        primary_key=("invoice_id",),
        columns={
            "invoice_id": "text",
            "order_id": "text",
            "issued_date": "date",
            "due_date": "date",
            "paid_date": "date",
            "amount": "numeric(14,2)",
            "status": "text",
            "updated_at": "timestamptz",
        },
        converters={"amount": as_decimal, "updated_at": as_timestamp},
    ),
)


def filter_incremental_rows(
    rows: list[dict[str, Any]], watermark: datetime | None, watermark_column: str
) -> list[dict[str, Any]]:
    if watermark is None:
        return rows
    return [row for row in rows if row[watermark_column] > watermark]


def _create_raw_table(connection: Connection, spec: SourceSpec) -> None:
    column_definitions = [
        sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(data_type))
        for name, data_type in spec.columns.items()
    ]
    primary_key = sql.SQL(", ").join(map(sql.Identifier, spec.primary_key))
    statement = sql.SQL(
        "CREATE TABLE IF NOT EXISTS raw.{} ({}, _ingested_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY ({}))"
    ).format(
        sql.Identifier(spec.table),
        sql.SQL(", ").join(column_definitions),
        primary_key,
    )
    with connection.cursor() as cursor:
        cursor.execute(statement)


def _read_csv(path: Path, spec: SourceSpec) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as source_file:
        rows = list(csv.DictReader(source_file))

    expected = set(spec.columns)
    if rows and set(rows[0]) != expected:
        raise ValueError(
            f"Colonnes invalides dans {path.name}: attendu {sorted(expected)}, "
            f"recu {sorted(rows[0])}"
        )

    converted: list[dict[str, Any]] = []
    for row in rows:
        converted.append(
            {
                column: (
                    None
                    if value == ""
                    else spec.converters.get(column, lambda item: item)(value)
                )
                for column, value in row.items()
            }
        )
    return converted


def _watermark(connection: Connection, source_name: str) -> datetime | None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT watermark FROM metadata.ingestion_state WHERE source_name = %s",
            (source_name,),
        )
        result = cursor.fetchone()
    return result[0] if result else None


def ingest_source(connection: Connection, data_dir: Path, spec: SourceSpec) -> int:
    _create_raw_table(connection, spec)
    rows = _read_csv(data_dir / spec.filename, spec)
    previous_watermark = _watermark(connection, spec.name)
    delta = filter_incremental_rows(rows, previous_watermark, spec.watermark_column)

    if delta:
        columns = list(spec.columns)
        placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
        update_columns = [column for column in columns if column not in spec.primary_key]
        updates = sql.SQL(", ").join(
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
            for column in update_columns
        )
        statement = sql.SQL(
            "INSERT INTO raw.{} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}, _ingested_at = now()"
        ).format(
            sql.Identifier(spec.table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders,
            sql.SQL(", ").join(map(sql.Identifier, spec.primary_key)),
            updates,
        )
        values = [[row[column] for column in columns] for row in delta]
        with connection.cursor() as cursor:
            cursor.executemany(statement, values)

    new_watermark = max(
        (row[spec.watermark_column] for row in delta),
        default=previous_watermark,
    )
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO metadata.ingestion_state
                (source_name, watermark, rows_ingested, last_run_at, status)
            VALUES (%s, %s, %s, now(), 'success')
            ON CONFLICT (source_name) DO UPDATE SET
                watermark = EXCLUDED.watermark,
                rows_ingested = EXCLUDED.rows_ingested,
                last_run_at = now(),
                status = 'success'
            """,
            (spec.name, new_watermark, len(delta)),
        )
    return len(delta)


def run_ingestion(settings: Settings | None = None) -> dict[str, int]:
    cfg = settings or Settings()
    results: dict[str, int] = {}
    with connect(cfg) as connection:
        initialise_schemas(connection)
        for spec in SOURCES:
            results[spec.name] = ingest_source(connection, cfg.data_dir, spec)
    return results

