import pytest
from main import calculate_total


@pytest.fixture
def default_rules():
    return {
        "volume_discounts": {5: 0.10, 10: 0.20},
        "bundle_categories": ["book"],
    }


def test_empty_cart(default_rules):
    assert calculate_total([], default_rules) == 0.0


def test_no_rules():
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 3},
        {"id": "B", "category": "tech", "price": 50.0, "qty": 1},
    ]
    assert calculate_total(cart, {}) == 80.0


def test_volume_discount_only():
    rules = {"volume_discounts": {5: 0.10, 10: 0.20}}
    cart = [
        {"id": "A", "category": "food", "price": 10.0, "qty": 5},  # -10% -> 9€ x 5 = 45€
        {"id": "B", "category": "food", "price": 10.0, "qty": 2},  # 10€ x 2 = 20€
    ]
    assert calculate_total(cart, rules) == 65.0


def test_bundle_exact_multiple_of_three(default_rules):
    cart = [
        {"id": "A", "category": "book", "price": 30.0, "qty": 1},
        {"id": "B", "category": "book", "price": 20.0, "qty": 1},
        {"id": "C", "category": "book", "price": 10.0, "qty": 1},  # Offert
    ]
    assert calculate_total(cart, default_rules) == 50.0


def test_bundle_two_full_groups(default_rules):
    cart = [
        {"id": "A", "category": "book", "price": 50.0, "qty": 1},
        {"id": "B", "category": "book", "price": 40.0, "qty": 1},
        {"id": "C", "category": "book", "price": 30.0, "qty": 1},  # Offert (groupe 1)
        {"id": "D", "category": "book", "price": 20.0, "qty": 1},
        {"id": "E", "category": "book", "price": 10.0, "qty": 1},
        {"id": "F", "category": "book", "price": 5.0, "qty": 1},   # Offert (groupe 2)
    ]
    assert calculate_total(cart, default_rules) == 120.0


def test_bundle_with_remainder(default_rules):
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]
    assert calculate_total(cart, default_rules) == 145.0


def test_cumulative_volume_and_bundle(default_rules):
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 6},  # -10% -> 9€ x 6
    ]
    # 6 livres à 9€ -> 2 gratuits -> 4 payés = 36.0€
    assert calculate_total(cart, default_rules) == 36.0


def test_rounding_float_precision(default_rules):
    cart = [
        {"id": "A", "category": "tech", "price": 19.99, "qty": 1},
        {"id": "B", "category": "tech", "price": 9.95, "qty": 1},
    ]
    assert calculate_total(cart, default_rules) == 29.94