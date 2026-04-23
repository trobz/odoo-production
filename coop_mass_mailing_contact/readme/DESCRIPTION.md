Automatically synchronize mailing list contacts with cooperative members.

This module adds an **Is Member Contact** flag on mailing lists. When enabled,
the list is kept in sync with active cooperative members (`res.partner` where
`is_member = True`):

- **Add contacts**: new members are automatically added to the mailing list as
  `mailing.contact` records.
- **Remove contacts**: contacts whose partner is no longer a member are
  removed from the list.

The synchronization runs daily via a scheduled action, or can be triggered
manually at any time.
