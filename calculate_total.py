"""Module de calcul du montant total du panier d'achat."""

from collections import defaultdict


def calculate_total(cart: list[dict], rules: dict) -> float:
    """Calcule le montant total avec remises volume et offres groupées."""
    volume_discounts = rules.get("volume_discounts", {})
    bundle_categories = set(rules.get("bundle_categories", []))
    category_units = defaultdict(list)

    # 1. Remise volume et éclatement par unité
    for item in cart:
        threshold = max((t for t in volume_discounts if item["qty"] >= t), default=None)
        rate = volume_discounts[threshold] if threshold else 0.0

        unit_price = item["price"] * (1.0 - rate)
        category_units[item["category"]].extend([unit_price] * item["qty"])

    # 2. Calcule le total
    total = 0.0
    for category, units in category_units.items():
        if category in bundle_categories:
            free_amount = 0.0
            for i in range(0, len(units) - len(units) % 3, 3):
                free_amount += min(units[i : i + 3]) # Le moins cher du paquet de 3

            total += sum(units) - free_amount
        else:
            total += sum(units)

    return round(total, 2)
