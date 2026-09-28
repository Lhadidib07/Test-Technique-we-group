"""Tests unitaires pour la fonction calculate_total."""

from decimal import Decimal

import pytest
from calculate_total import calculate_total


@pytest.fixture(name="rules")
def default_rules():
    """Fournit les règles de promotion par défaut."""
    return {
        "volume_discounts": {5: 0.10, 10: 0.20},
        "bundle_categories": ["book"],
    }


def test_empty_cart(rules):
    """Panier vide : total attendu à 0.00."""
    assert calculate_total([], rules) == Decimal("0.00")


def test_no_rules():
    """Aucune règle : somme brute des articles."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 3},
        {"id": "B", "category": "tech", "price": 50.0, "qty": 1},
    ]
    assert calculate_total(cart, {}) == Decimal("80.00")


def test_volume_discount_only():
    """Remise sur volume seule selon les seuils atteints."""
    custom_rules = {"volume_discounts": {5: 0.10, 10: 0.20}}
    cart = [
        {"id": "A", "category": "food", "price": 10.0, "qty": 5},  # -10% -> 9€ x 5 = 45€
        {"id": "B", "category": "food", "price": 10.0, "qty": 2},  # 10€ x 2 = 20€
    ]
    assert calculate_total(cart, custom_rules) == Decimal("65.00")


def test_bundle_exact_multiple_of_three(rules):
    """Lot exact de 3 : le moins cher est offert."""
    cart = [
        {"id": "A", "category": "book", "price": 30.0, "qty": 1},
        {"id": "B", "category": "book", "price": 20.0, "qty": 1},
        {"id": "C", "category": "book", "price": 10.0, "qty": 1},  # Offert
    ]
    assert calculate_total(cart, rules) == Decimal("50.00")


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
    assert calculate_total(cart, rules) == Decimal("120.00")


def test_bundle_with_remainder(rules):
    """Lot de 3 avec articles restants hors promotion."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]
    assert calculate_total(cart, rules) == Decimal("145.00")


def test_cumulative_volume_and_bundle(rules):
    """Cumul de la remise sur volume et de l'offre 3 pour 2."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 6},  # -10% -> 9€ x 6
    ]
    # 6 livres à 9€ -> 2 gratuits -> 4 payés = 36.00€
    assert calculate_total(cart, rules) == Decimal("36.00")


def test_rounding_float_precision(rules):
    """Arrondi à 2 décimales sur des prix fractionnaires."""
    cart = [
        {"id": "A", "category": "tech", "price": 19.99, "qty": 1},
        {"id": "B", "category": "tech", "price": 9.95, "qty": 1},
    ]
    assert calculate_total(cart, rules) == Decimal("29.94")


def test_bundle_respects_cart_arrival_order(rules):
    """Respect strict de l'ordre d'arrivée pour les paquets de 3."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 2},
        {"id": "B", "category": "book", "price": 50.0, "qty": 1},
        {"id": "C", "category": "book", "price": 40.0, "qty": 3},
    ]
    assert calculate_total(cart, rules) == Decimal("140.00")


def test_huge_quantities_performance(rules):
    """Vérifie que les quantités gigantesques s'exécutent en temps constant sans OOM."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 3_000_000_000_001},
        {"id": "B", "category": "book", "price": 20.0, "qty": 2},
    ]
    # Seuil 10 atteint -> remise volume 20% -> livre A à 8.00€
    # Livre B (qty 2 < 5) -> 0% remise -> 20.00€
    # Livre A : 3_000_000_000_001 // 3 = 1_000_000_000_000 bundles complets
    #           -> 2_000_000_000_000 payés = 16_000_000_000_000€
    # Reste de A : 1 exemplaire à 8.00€
    # Reste de B : 2 exemplaires à 20.00€
    # Trio mixte : [8.00, 20.00, 20.00] -> le moins cher (8.00€) est offert
    #              Total payé trio = 40.00€
    # Total attendu : 16_000_000_000_040.00€
    assert calculate_total(cart, rules) == Decimal("16000000000040.00")


def test_bundle_mixed_remainders_across_three_items(rules):
    """Trois articles différents avec qty=1 forment ensemble un lot de 3."""
    cart = [
        {"id": "A", "category": "book", "price": 15.0, "qty": 1},
        {"id": "B", "category": "book", "price": 30.0, "qty": 1},
        {"id": "C", "category": "book", "price": 25.0, "qty": 1},
    ]
    # Total brut : 15 + 30 + 25 = 70€
    # Moins cher offert : 15€ -> Total : 55.00€
    assert calculate_total(cart, rules) == Decimal("55.00")


def test_zero_quantity_item(rules):
    """Un article avec qty=0 ne doit pas impacter le calcul ni lever d'erreur."""
    cart = [
        {"id": "A", "category": "book", "price": 20.0, "qty": 0},
        {"id": "B", "category": "tech", "price": 50.0, "qty": 1},
    ]
    assert calculate_total(cart, rules) == Decimal("50.00")


def test_bundle_interleaved_with_other_categories(rules):
    """Les articles hors promotion intercalés ne perturbent pas le lot de la catégorie cible."""
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 1},
        {"id": "T1", "category": "tech", "price": 100.0, "qty": 1},
        {"id": "B", "category": "book", "price": 20.0, "qty": 1},
        {"id": "T2", "category": "tech", "price": 50.0, "qty": 1},
        {"id": "C", "category": "book", "price": 15.0, "qty": 1},
    ]
    # Tech : 100 + 50 = 150€
    # Livres : 10 + 20 + 15 = 45€ - min(10, 20, 15) [10€] = 35€
    # Total attendu : 185.00€
    assert calculate_total(cart, rules) == Decimal("185.00")


def test_precision_loss_without_decimal():
    """Valide l'évitement du bug d'arrondi des flottants IEEE 754.

    En float standard :
    - 2.675 n'est pas représentable exactement (2.67499999999999982236...).
    - round(2.675, 2) retourne 2.67 au lieu de 2.68.
    Avec Decimal et ROUND_HALF_UP, 2.675 est arrondi correctement à 2.68.
    """
    cart = [
        {"id": "A", "category": "food", "price": 2.675, "qty": 1},
    ]
    assert calculate_total(cart, {}) == Decimal("2.68")


def test_float_accumulation_imprecision():
    """Valide qu'une accumulation répétée de centimes ne dérive pas.

    En float standard :
    sum([0.1] * 10) != 1.0 (vaut 0.9999999999999999).
    Avec Decimal, la somme de 70 x 0.10€ et 30 x 0.20€ vaut exactement 13.00€.
    """
    cart = [
        {"id": "A", "category": "stationery", "price": 0.10, "qty": 70},
        {"id": "B", "category": "stationery", "price": 0.20, "qty": 30},
    ]
    assert calculate_total(cart, {}) == Decimal("13.00")
