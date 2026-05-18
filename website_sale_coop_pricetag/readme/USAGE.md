# Website Sale Coop Pricetag — Usage

Module: `website_sale_coop_pricetag`

## Overview

This module extends the e-commerce product page to display the unit price per kilogram
and/or per liter next to the standard sale price.

The values are computed automatically from `coop_default_pricetag`:

- `price_weight = list_price / weight` (shown as €/kg)
- `price_volume = list_price / volume` (shown as €/L)

## Dependencies

- `website_sale`
- `coop_default_pricetag`

## Configuration

No specific configuration required. The pricetag is displayed automatically
based on the product's **Weight** and **Volume** fields.

### Setting weight and volume on a product

1. Go to *Website* → *eCommerce* → *Products* (or *Sales* → *Products*).
2. Open a product.
3. Go to the **General Information** tab:
   - Set **Weight** (kg) — e.g. `0.5` for 500 g.
   - Set **Volume** (L) — e.g. `0.75` for 750 mL.
4. Save.

The computed fields `price_weight` and `price_volume` update automatically.

## Display logic

On the product page (`/shop/<product>`), the pricetag span appears:

| Condition | Displayed |
|-----------|-----------|
| `weight > 0` only | `(€X.XX /kg)` |
| `volume > 0` only | `(€X.XX /L)` |
| both `weight > 0` and `volume > 0` | `(€X.XX /kg or €X.XX /L)` |
| neither | nothing shown |

## Troubleshooting

- **Pricetag not visible** — Check that the product has a non-zero **Weight** or **Volume**.
- **Price shown as 0** — Ensure `list_price` is set and greater than 0.
