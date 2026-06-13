Global UI customizations applied to all foodcoop instances.

## Features

### List view — column header text wrapping

By default Odoo truncates long column header labels in list views. This
module forces headers to wrap at word boundaries so that labels like
*Conditionnement indicatif hors taxes* or *Prix de vente TTC* are always
fully readable without hovering.

- Column `<th>` elements are set to `overflow: visible` and
  `white-space: normal`.
- Inner `.o_column_header` and `.text-truncate` elements additionally get
  `word-break: break-word` so that single long words also wrap rather than
  overflow.

### List view — text cell wrapping

For character (`o_list_char`) and many2one (`o_list_many2one`) data cells,
text wraps instead of being clipped. This prevents long product names or
partner names from being silently truncated in read-only rows.
