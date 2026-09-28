"""Module de calcul du montant total du panier d'achat."""

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal


def calculate_total(cart: list[dict], rules: dict) -> Decimal:
    """Calcule le montant total avec remises volume et offres groupées."""
    thresholds = sorted(rules.get("volume_discounts", {}).items())
    bundle_categories = set(rules.get("bundle_categories", []))

    bundle_lines = defaultdict(list)
    total = Decimal(0)

    # 1. Total brut et constitution des lignes bundle
    for item in cart:
        rate = Decimal(0)
        for threshold, discount in thresholds:
            if item["qty"] >= threshold:
                rate = Decimal(str(discount))

        unit_price = Decimal(str(item["price"])) * (Decimal(1) - rate)
        total += unit_price * item["qty"]

        if item["category"] in bundle_categories:
            bundle_lines[item["category"]].append((unit_price, item["qty"]))

    # 2. Une seule boucle par catégorie éligible
    for lines in bundle_lines.values():
        pending_units = []

        for unit_price, qty in lines:
            # Lots complets du même article
            total -= unit_price * (qty // 3) # 3 // 3 = 1 paquet complet

            # Reste (1 ou 2) ajouté à la suite
            pending_units.extend([unit_price] * (qty % 3))

            # Si on forme un paquet de 3, on retire le moins cher
            if len(pending_units) >= 3:
                total -= min(pending_units[:3]) # min des 3 premiers
                pending_units = pending_units[3:] # extraire apres les 3 premiers

    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
