import pytest

from pme_data_stack.quality import assert_quality


def test_quality_accepts_passing_checks():
    assert_quality([{"check": "test", "status": "pass"}])


def test_quality_raises_with_failed_check_name():
    with pytest.raises(RuntimeError, match="orphelins"):
        assert_quality([{"check": "orphelins", "status": "fail"}])

