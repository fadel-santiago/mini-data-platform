from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from .ingestion import run_ingestion
from .quality import assert_quality, run_quality_checks


PROJECT_DIR = Path(__file__).resolve().parents[2]


def run_dbt(command: str = "build") -> None:
    profiles_dir = os.getenv("DBT_PROFILES_DIR", str(PROJECT_DIR))
    subprocess.run(
        ["dbt", command, "--project-dir", str(PROJECT_DIR), "--profiles-dir", profiles_dir],
        check=True,
    )


def run_pipeline() -> None:
    ingestion = run_ingestion()
    print(json.dumps({"ingestion": ingestion}, indent=2, ensure_ascii=False))
    run_dbt("build")
    quality = run_quality_checks()
    print(json.dumps({"quality": quality}, indent=2, ensure_ascii=False))
    assert_quality(quality)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline data PME")
    parser.add_argument(
        "command",
        choices=("ingest", "transform", "quality", "pipeline"),
        help="Etape a executer",
    )
    args = parser.parse_args()

    if args.command == "ingest":
        print(json.dumps(run_ingestion(), indent=2, ensure_ascii=False))
    elif args.command == "transform":
        run_dbt("build")
    elif args.command == "quality":
        results = run_quality_checks()
        print(json.dumps(results, indent=2, ensure_ascii=False))
        assert_quality(results)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()

