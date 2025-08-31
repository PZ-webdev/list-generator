from app.utils.validator import validate_number


def test_validate_number_allows_empty_and_digits():
    v = validate_number(999)
    assert v('') is True
    assert v('0') is True
    assert v('123') is True
    assert v('999') is True


def test_validate_number_bounds_and_invalid():
    v = validate_number(10)
    assert v('11') is False
    assert v('-1') is False
    assert v('abc') is False
