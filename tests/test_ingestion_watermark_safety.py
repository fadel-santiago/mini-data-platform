"""Synthetic CSV regressions; storage is simulated, not a PostgreSQL integration test."""

import csv
from contextlib import contextmanager

import pytest

from pme_data_stack.ingestion import SourceSpec, as_timestamp, ingest_source


SPEC = SourceSpec(
    name="synthetic_records",
    filename="synthetic.csv",
    table="synthetic_records",
    primary_key=("id",),
    columns={"id": "text", "label": "text", "updated_at": "timestamptz"},
    converters={"updated_at": as_timestamp},
)


class MemoryStorage:
    """Only the cursor operations used by ingest_source; never opens a database."""

    def __init__(self):
        self.watermark = None
        self.rows = {}
        self.rows_ingested = None

    @contextmanager
    def cursor(self):
        yield MemoryCursor(self)


class MemoryCursor:
    def __init__(self, storage):
        self.storage = storage

    def execute(self, statement, parameters=None):
        query = statement if isinstance(statement, str) else statement.as_string()
        query = query.strip()
        if query.startswith("CREATE TABLE IF NOT EXISTS raw."):
            return
        if query.startswith("SELECT watermark FROM metadata.ingestion_state"):
            assert parameters == (SPEC.name,)
            return
        assert query.startswith("INSERT INTO metadata.ingestion_state")
        source, watermark, count = parameters
        assert source == SPEC.name
        self.storage.watermark = watermark
        self.storage.rows_ingested = count

    def fetchone(self):
        return (self.storage.watermark,)

    def executemany(self, statement, values):
        # Model the existing unconditional primary-key upsert, not arbitrary SQL.
        assert "ON CONFLICT" in statement.as_string()
        for values_row in values:
            row = dict(zip(SPEC.columns, values_row))
            self.storage.rows[row["id"]] = row


def snapshot(directory, *records):
    with (directory / SPEC.filename).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SPEC.columns))
        writer.writeheader()
        writer.writerows(
            {"id": key, "label": label, "updated_at": f"2026-10-{day:02d}T00:00:00Z"}
            for key, label, day in records
        )


def test_first_load_and_unchanged_replay(tmp_path):
    storage = MemoryStorage()
    snapshot(tmp_path, ("A", "current", 10))
    assert ingest_source(storage, tmp_path, SPEC) == 1
    assert ingest_source(storage, tmp_path, SPEC) == 0
    assert storage.watermark == as_timestamp("2026-10-10T00:00:00Z")
    assert storage.rows_ingested == 0
    assert len(storage.rows) == 1


@pytest.mark.parametrize("existing_day", [None, 10])
def test_empty_snapshot_preserves_watermark(tmp_path, existing_day):
    storage = MemoryStorage()
    if existing_day is not None:
        snapshot(tmp_path, ("A", "current", existing_day))
        ingest_source(storage, tmp_path, SPEC)
    previous_watermark = storage.watermark
    previous_rows = storage.rows.copy()
    snapshot(tmp_path)
    assert ingest_source(storage, tmp_path, SPEC) == 0
    assert storage.watermark == previous_watermark
    assert storage.rows == previous_rows


def test_mixed_snapshot_ingests_only_newer_records(tmp_path):
    storage = MemoryStorage()
    snapshot(tmp_path, ("A", "current", 10))
    ingest_source(storage, tmp_path, SPEC)
    snapshot(tmp_path, ("A", "stale", 5), ("B", "new", 11))
    assert ingest_source(storage, tmp_path, SPEC) == 1
    assert storage.rows["A"]["label"] == "current"
    assert storage.rows["B"]["label"] == "new"
    assert storage.watermark == as_timestamp("2026-10-11T00:00:00Z")


def test_older_snapshot_must_not_lower_watermark(tmp_path):
    storage = MemoryStorage()
    snapshot(tmp_path, ("A", "current", 10))
    ingest_source(storage, tmp_path, SPEC)
    previous_watermark = storage.watermark
    snapshot(tmp_path, ("A", "older", 5))
    assert ingest_source(storage, tmp_path, SPEC) == 0
    assert storage.rows["A"]["label"] == "current"
    assert storage.watermark == previous_watermark


def test_older_snapshots_must_not_overwrite_a_newer_record(tmp_path):
    storage = MemoryStorage()
    for label, day in [("current", 10), ("older", 5), ("intermediate", 7)]:
        snapshot(tmp_path, ("A", label, day))
        ingest_source(storage, tmp_path, SPEC)
    assert storage.rows["A"]["label"] == "current"
    assert storage.rows["A"]["updated_at"] == as_timestamp("2026-10-10T00:00:00Z")
