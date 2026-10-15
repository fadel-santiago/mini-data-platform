from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg import Connection

from .config import Settings


@contextmanager
def connect(settings: Settings | None = None) -> Iterator[Connection]:
    cfg = settings or Settings()
    with psycopg.connect(cfg.dsn) as connection:
        yield connection


def initialise_schemas(connection: Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS metadata")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS observability")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata.ingestion_state (
                source_name text PRIMARY KEY,
                watermark timestamptz,
                rows_ingested integer NOT NULL DEFAULT 0,
                last_run_at timestamptz NOT NULL DEFAULT now(),
                status text NOT NULL DEFAULT 'success'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS observability.quality_results (
                id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                check_name text NOT NULL,
                status text NOT NULL CHECK (status IN ('pass', 'fail')),
                observed_value numeric,
                threshold text,
                checked_at timestamptz NOT NULL DEFAULT now(),
                details text
            )
            """
        )

