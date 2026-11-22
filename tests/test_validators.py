import pytest
from validators import validate_complaint

def test_valid_input():
    assert validate_complaint("C-1", "Need help") == ("C-1", "Need help")

def test_empty_text_rejected():
    with pytest.raises(ValueError):
        validate_complaint("C-1", " ")

def test_empty_customer_rejected():
    with pytest.raises(ValueError):
        validate_complaint("", "Need help")
