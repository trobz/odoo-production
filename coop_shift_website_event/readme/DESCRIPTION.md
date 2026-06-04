This module adds a compatibility override for `shift.shift` when
`website_event` is installed.

`website_event` menu synchronization assumes `event.event` recordsets, while
`coop_shift` stores the concrete records on `shift.shift`.

The override keeps the menu update recordsets on `shift.shift` to avoid mixed
recordset unions during writes.