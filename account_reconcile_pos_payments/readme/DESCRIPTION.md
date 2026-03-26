This module adds assisted reconciliation flows for bank statements:

* Automatic matching of bank expense lines based on regex patterns configured
	on the journal.
* Automatic matching of POS payment lines against child POS statements,
	including optional contactless 2-lines combination matching.

When a match is found, the module updates statement line counterpart accounts
and reconciles the related journal items.
