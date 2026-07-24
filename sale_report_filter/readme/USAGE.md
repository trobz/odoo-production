Once installed, this module automatically configures the Sales Analysis report with today's date filter.

**Accessing the Sales Analysis Report**:

1. Go to **Sales > Reporting > Sales**
2. The report will automatically display with:
   - Today's sales data filtered
   - Pivot view showing key metrics (quantity, price total, subtotal, count)

**Using the Today Filter Manually**:

1. In the Sales Analysis report, click on **Filters**
2. Find and select **Order Date: Today** from the filter list
3. The report will refresh to show only today's sales orders

**Viewing Other Date Ranges**:

To view sales from different periods:
1. Remove the "Order Date: Today" filter (click the X on the filter tag)
2. Use other date filters available in the Filters dropdown:
   - Order Month
   - Order Year
   - Custom date ranges

**Customizing Pivot Measures**:

The default pivot measures are pre-configured, but you can customize them:
1. In the pivot view, click on **Measures**
2. Select or deselect the metrics you want to display:
   - Quantity (product_uom_qty)
   - Total (price_total)
   - Untaxed Total (price_subtotal)
   - Count

**Switching Views**:

The Sales Analysis report supports multiple views:
- **Pivot**: Matrix view with aggregated data (default)
- **Graph**: Visual charts of sales data
- **List**: Detailed line-by-line view

**Note**: The Today filter uses UTC timezone conversion to accurately display sales for the current calendar day based on your timezone settings.
