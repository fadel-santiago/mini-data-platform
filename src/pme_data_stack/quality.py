from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from psycopg import Connection

from .config import Settings
from .db import connect, initialise_schemas


@dataclass(frozen=True)
class QualityCheck:
    name: str
    query: str
    expected: str
    passes: Callable[[Any], bool]


CHECKS = (
    QualityCheck(
        "commandes_sans_client",
        """
        SELECT count(*)
        FROM raw.orders o
        LEFT JOIN raw.customers c USING (customer_id)
        WHERE c.customer_id IS NULL
        """,
        "0",
        lambda value: value == 0,
    ),
    QualityCheck(
        "lignes_sans_commande",
        """
        SELECT count(*)
        FROM raw.order_lines l
        LEFT JOIN raw.orders o USING (order_id)
        WHERE o.order_id IS NULL
        """,
        "0",
        lambda value: value == 0,
    ),
    QualityCheck(
        "montants_factures_negatifs",
        "SELECT count(*) FROM raw.invoices WHERE amount < 0",
        "0",
        lambda value: value == 0,
    ),
    QualityCheck(
        "marges_incoherentes",
        """
        SELECT count(*)
        FROM marts.sales_orders
        WHERE gross_margin <> revenue - cost_of_goods
           OR revenue < 0
        """,
        "0",
        lambda value: value == 0,
    ),
    QualityCheck(
        "sources_recentes_heures",
        """
        SELECT extract(epoch FROM (now() - min(last_run_at))) / 3600
        FROM metadata.ingestion_state
        """,
        "<= 24",
        lambda value: value is not None and value <= Decimal("24"),
    ),
)


def run_quality_checks(settings: Settings | None = None) -> list[dict[str, object]]:
    cfg = settings or Settings()
    results: list[dict[str, object]] = []
    with connect(cfg) as connection:
        initialise_schemas(connection)
        for check in CHECKS:
            with connection.cursor() as cursor:
                cursor.execute(check.query)
                observed = cursor.fetchone()[0]
                status = "pass" if check.passes(observed) else "fail"
                cursor.execute(
                    """
                    INSERT INTO observability.quality_results
                        (check_name, status, observed_value, threshold, details)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        check.name,
                        status,
                        observed,
                        check.expected,
                        f"Valeur observee: {observed}",
                    ),
                )
            results.append(
                {
                    "check": check.name,
                    "status": status,
                    "observed": str(observed),
                    "expected": check.expected,
                }
            )
    return results


def assert_quality(results: list[dict[str, object]]) -> None:
    failed = [result for result in results if result["status"] == "fail"]
    if failed:
        names = ", ".join(str(result["check"]) for result in failed)
        raise RuntimeError(f"Controles qualite en echec: {names}")

