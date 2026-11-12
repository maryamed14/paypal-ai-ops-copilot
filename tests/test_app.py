from app.analysis import fallback
from app.main import health, NewOrder
import pytest
from pydantic import ValidationError

def test_health():
    assert health()['environment'] == 'sandbox'

def test_pending_requires_review():
    result = fallback('PENDING')
    assert result.requires_human_review
    assert 'does not establish' in result.explanation

def test_completed_no_review():
    assert fallback('COMPLETED').requires_human_review is False

def test_invalid_amount():
    with pytest.raises(ValidationError):
        NewOrder(amount='-10')
