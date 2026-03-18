# Coop Default Price Tag — Usage

Module: `coop_default_pricetag`

## Overview

`coop_default_pricetag` extends the printing flow from `product_print_category` to print price tags (pricetags) for products using QWeb reports.

Key points:

- Price tag templates are defined as QWeb reports (several variants are provided).
- Each *Print Category* can be linked to a *Pricetag Model* which determines which report template to use.
- A wizard (`product.print.wizard`) collects products to print and generates the report.
- After printing, selected products are marked as printed by setting `to_print = False`.

## Installation

- Install the module **Coop Default Price Tag**.
- Ensure dependencies are installed:

  - `product`
  - `product_print_category`
  - `purchase_package_qty`

## Permissions

- **Manage Food fields** (`coop_default_pricetag.group_food_manager`)

  - Implies `product_print_category.manager`.
  - Grants access to additional “Food Informations” and “Price Tag” fields on the product form.

## Configuration

### 1) Configure Paper Formats

The module provides default paper formats:

- **Default pricetag paper** (`coop_default_pricetag.paperformat_pricetag`)
- **Vegetables pricetag paper** (`coop_default_pricetag.paperformat_pricetag_vegetables`)

You can review them in Odoo:

- *Settings* -> *Technical* -> *Reports* -> *Paper Format*

### 2) Configure Pricetag Models

A **Pricetag Model** links:

- A paper format (`report.paperformat`)
- A report template identifier (`report_model`), i.e. the `report_name` of an `ir.actions.report`

Menu:

- *Sales* -> *Configuration* -> *Pricetag Model*

Provided records (examples):

- **Default pricetag model** -> `coop_default_pricetag.report_pricetag`
- **Default pricetag model with barcode** -> `coop_default_pricetag.report_pricetag_barcode`
- **Vegetables pricetag model** -> `coop_default_pricetag.report_pricetag_vegetables`
- **Small Pricetag with Barcode** -> `coop_default_pricetag.report_pricetag_simple_barcode`

### 3) Configure Product Print Categories

Each **Product Print Category** can be assigned a **Pricetag Model**.

In the *Product Print Category* form view, a new field is available:

- `Pricetag Model`

This is the field used by the printing wizard to decide which report to generate.

## Printing Pricetags

### Entry points (menus)

This module adds additional product list menus under Purchasing:

- *Purchase* -> *Products* -> **Products (Food)**
- *Purchase* -> *Products* -> **Products (Origin)**
- *Purchase* -> *Products* -> **Products (Price Tags)**

The **Products (Price Tags)** action opens a list view with a default search context `search_default_print_todo=1` (typically showing products still to print, depending on `product_print_category` configuration).

### Typical printing flow

1. Open the products list (for example **Products (Price Tags)**).
2. Select products to print.
3. Use the print action from `product_print_category` (opens the *Print Wizard*).
4. In the wizard:

   - Lines are grouped by *Print Category*.
   - Quantity determines how many labels will be generated per product.

5. Click **Print**.

What happens under the hood:

- The wizard checks the *Print Category* (from the first wizard line) and takes `print_category.pricetag_model_id.report_model`.
- It searches an `ir.actions.report` with `report_name` matching that value.
- It executes that report.
- Finally, it sets `to_print` to `False` on printed products.

## Product fields used in pricetags

The provided report templates reference several product fields.

### Fields shown on QWeb pricetags

Common fields used by templates:

- `name`
- `list_price`
- `barcode`
- `code` (in templates; depends on your database / other modules)
- `weight` and computed `price_weight` (`list_price / weight`)
- `volume` and computed `price_volume` (`list_price / volume`)
- `pricetag_origin` (computed from `country_id`, `origin_description`, `maker_description`)
- `pricetag_rackinfos` (computed from rack fields and vendor package quantity if available)
- `pricetag_coopinfos` (computed from `farming_method` and `other_information`)

### Editing Food/Origin/Pricetag information

On the product form (`product.template`), this module adds:

- A **Food Informations** page (visible for *Manage Food fields* group)
  - Origin: `country_id`, `origin_description`, `maker_description`
  - Food: `fresh_category`, `fresh_range`, `is_mercuriale`, `label_ids`
  - Price Tag: `expiration_date_days`, `expiration_comsumption_days`, extra notes, `ingredients`

Also, it adds extra fields in the main form:

- `price_weight`
- `price_volume`
- Pricetag Information group: `rack_instruction`, `rack_location`, `rack_number_of_packages`, `farming_method`, `other_information`

## Labels

The module introduces `product.label`:

Menu:

- *Purchase* -> *Products* -> **Labels**

Purpose:

- Manage label records with an optional image and a `scale_logo_code`.
- Selecting labels on a product can update the product’s `scale_logo_code`.

A sample label is included:

- **Eurofeuille** (`EUROFEUILLE`) with `scale_logo_code = 14`.

## Reports provided

QWeb templates:

- `coop_default_pricetag.report_pricetag`
- `coop_default_pricetag.report_pricetag_barcode`
- `coop_default_pricetag.report_pricetag_simple_barcode`
- `coop_default_pricetag.report_pricetag_vegetables`

Notes:

- Barcode templates generate the barcode image via `/report/barcode` using EAN13.

## Troubleshooting

- **Wrong template printed**

  - Check the product’s *Print Category*.
  - Check that the *Print Category* has the correct **Pricetag Model** set.
  - Check that the `Pricetag Model` field `report_model` matches an existing `ir.actions.report.report_name`.

- **Barcode not shown**

  - Ensure the product has `barcode` set.
  - Ensure the barcode value matches expected format for EAN13 (depending on your barcode settings/policy).

- **Products disappear from “to print” list after printing**

  - Expected: printing sets `to_print = False` on printed products.
