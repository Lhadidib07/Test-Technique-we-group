"""Tests unitaires pour la fonction calculate_total."""

import pytest
from calculate import calculate_total


@pytest.fixture(name="rules")
def default_rules():
    """Fournit les règles de promotion par défaut."""
    return {
        "volume_discounts": {5: 0.10, 10: 0.20},
        "bundle_categories": ["book"],
    }


def test_empty_cart(rules):
    """Panier vide : total attendu à 0.0."""
    assert calculate_total([], rules) == 0.0


def test_no_rules():
    """Aucune règle : somme brute des articles."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 3},
        {"id": "B", "category": "tech", "price": 50.0, "qty": 1},
    ]
    assert calculate_total(cart, {}) == 80.0


def test_volume_discount_only():
    """Remise sur volume seule selon les seuils atteints."""
    custom_rules = {"volume_discounts": {5: 0.10, 10: 0.20}}
    cart = [
        {"id": "A", "category": "food", "price": 10.0, "qty": 5},  # -10% -> 9€ x 5 = 45€
        {"id": "B", "category": "food", "price": 10.0, "qty": 2},  # 10€ x 2 = 20€
    ]
    assert calculate_total(cart, custom_rules) == 65.0


def test_bundle_exact_multiple_of_three(rules):
    """Lot exact de 3 : le moins cher est offert."""
    cart = [
        {"id": "A", "category": "book", "price": 30.0, "qty": 1},
        {"id": "B", "category": "book", "price": 20.0, "qty": 1},
        {"id": "C", "category": "book", "price": 10.0, "qty": 1},  # Offert
    ]
    assert calculate_total(cart, rules) == 50.0


def test_bundle_two_full_groups(rules):
    """Deux lots complets de 3 avec déduction par lot."""
    cart = [
        {"id": "A", "category": "book", "price": 50.0, "qty": 1},
        {"id": "B", "category": "book", "price": 40.0, "qty": 1},
        {"id": "C", "category": "book", "price": 30.0, "qty": 1},  # Offert (groupe 1)
        {"id": "D", "category": "book", "price": 20.0, "qty": 1},
        {"id": "E", "category": "book", "price": 10.0, "qty": 1},
        {"id": "F", "category": "book", "price": 5.0, "qty": 1},   # Offert (groupe 2)
    ]
    assert calculate_total(cart, rules) == 120.0


def test_bundle_with_remainder(rules):
    """Lot de 3 avec articles restants hors promotion."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]
    assert calculate_total(cart, rules) == 145.0


def test_cumulative_volume_and_bundle(rules):
    """Cumul de la remise sur volume et de l'offre 3 pour 2."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 6},  # -10% -> 9€ x 6
    ]
    # 6 livres à 9€ -> 2 gratuits -> 4 payés = 36.0€
    assert calculate_total(cart, rules) == 36.0


def test_rounding_float_precision(rules):
    """Arrondi à 2 décimales sur des prix fractionnaires."""
    cart = [
        {"id": "A", "category": "tech", "price": 19.99, "qty": 1},
        {"id": "B", "category": "tech", "price": 9.95, "qty": 1},
    ]
    assert calculate_total(cart, rules) == 29.94


def test_bundle_respects_cart_arrival_order(rules):
    """Respect strict de l'ordre d'arrivée pour les paquets de 3."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 2},
        {"id": "B", "category": "book", "price": 50.0, "qty": 1},
        {"id": "C", "category": "book", "price": 40.0, "qty": 3},
    ]

    # Total brut : (2 x 10) + 50 + (3 x 40) = 20 + 50 + 120 = 190.0€
    # Déductions : 10€ (lot 1) + 40€ (lot 2) = 50.0€
    # Total attendu : 190.0 - 50.0 = 140.0€
    assert calculate_total(cart, rules) == 140.0
