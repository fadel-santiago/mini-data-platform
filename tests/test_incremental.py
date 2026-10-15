from datetime import datetime, timezone

from pme_data_stack.ingestion import filter_incremental_rows


def test_first_load_keeps_all_rows():
    rows = [{"updated_at": datetime(2026, 10, 1, tzinfo=timezone.utc)}]
    assert filter_incremental_rows(rows, None, "updated_at") == rows


def test_incremental_load_only_keeps_strictly_newer_rows():
    watermark = datetime(2026, 10, 5, tzinfo=timezone.utc)
    old = {"id": 1, "updated_at": datetime(2026, 10, 5, tzinfo=timezone.utc)}
    new = {"id": 2, "updated_at": datetime(2026, 10, 6, tzinfo=timezone.utc)}
    assert filter_incremental_rows([old, new], watermark, "updated_at") == [new]

