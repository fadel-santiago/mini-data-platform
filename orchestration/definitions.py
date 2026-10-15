from __future__ import annotations

import json

from dagster import Definitions, ScheduleDefinition, get_dagster_logger, job, op

from pme_data_stack.cli import run_dbt
from pme_data_stack.ingestion import run_ingestion
from pme_data_stack.quality import assert_quality, run_quality_checks


@op
def ingest_incremental() -> dict[str, int]:
    result = run_ingestion()
    get_dagster_logger().info("Ingestion: %s", json.dumps(result))
    return result


@op
def build_analytics(ingestion_result: dict[str, int]) -> str:
    get_dagster_logger().info(
        "Construction dbt apres %s nouvelles lignes", sum(ingestion_result.values())
    )
    run_dbt("build")
    return "dbt build termine"


@op
def observe_quality(transform_status: str) -> list[dict[str, object]]:
    get_dagster_logger().info("Controle qualite apres: %s", transform_status)
    result = run_quality_checks()
    assert_quality(result)
    return result


@job(description="Ingestion incrementale, modeles dbt et controles qualite")
def pme_daily_pipeline():
    observe_quality(build_analytics(ingest_incremental()))


daily_schedule = ScheduleDefinition(
    job=pme_daily_pipeline,
    cron_schedule="0 6 * * *",
    execution_timezone="Europe/Paris",
)


defs = Definitions(jobs=[pme_daily_pipeline], schedules=[daily_schedule])

