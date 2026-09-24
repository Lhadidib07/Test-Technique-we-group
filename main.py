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

    # 2) Calcule le total
    total = 0.0
    for category, units in category_units.items():
        if category in bundle_categories:
            free_amount = 0.0
            for i in range(0, len(units) - len(units) % 3, 3):
                free_amount += min(units[i : i + 3])  # Le moins cher du paquet de 3

            total += sum(units) - free_amount
        else:
            total += sum(units)

    return round(total, 2)


if __name__ == "__main__":
    demo_rules = {
        "volume_discounts": {5: 0.10, 10: 0.20},  # qty >= 5: -10%, qty >= 10: -20%
        "bundle_categories": ["book"],  # 3e offert par tranche de 3
    }
    demo_cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]

    assert calculate_total(demo_cart, demo_rules) == 145.00
    result = calculate_total(demo_cart, demo_rules)
    print(f"Total calculé : {result}")
