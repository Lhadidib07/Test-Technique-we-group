"""Point d'entrée principal pour la démonstration."""

from calculate_total import calculate_total

rules = {
    "volume_discounts": {5: 0.10, 10: 0.20},
    "bundle_categories": ["book"],
}
sample_cart = [
    {"id": "A", "category": "book", "price": 10.0, "qty": 4},
    {"id": "B", "category": "book", "price": 15.0, "qty": 1},
    {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
]

total = calculate_total(sample_cart, rules)
print(f"Total calculé : {total}€")
