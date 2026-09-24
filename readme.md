# Cart Total Calculator

Module Python permettant de calculer le montant total d'un panier d'achat en appliquant des remises sur volume et des offres promotionnelles groupées (*3 pour 2*).

---

## Fonctionnalités

1. **Remise sur volume (Règle 1)** :
   - Définie par des seuils de quantité par ligne d'article (`volume_discounts`).
   - Applique le taux de remise maximal atteint directement sur le prix unitaire.

2. **Offre groupée « 3 pour 2 » (Règle 2)** :
   - Active uniquement sur les catégories listées dans `bundle_categories`.
   - Regroupe les articles par **lots séquentiels de 3 selon leur ordre d'arrivée** dans le panier.
   - Dans chaque lot complet de 3 unités, l'article le moins cher est offert.
   - Les articles restants ne formant pas un lot complet sont facturés au tarif normal.

3. **Arrondi monétaire** :
   - Le montant final est systématiquement arrondi à deux décimales (`round(..., 2)`).

---
```bash
pip install pytest
```
## Structure du projet

```text
.
├── main.py              # Logique métier (fonction calculate_total)
├── tests/
│   └── test_cart.py     # Suite de tests unitaires
└── README.md