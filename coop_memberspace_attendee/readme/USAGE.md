Once the module is installed, the "Expected attendees" column appears
automatically on the shift registration pages — no configuration is required.

## Programmer un extra (extra shift booking)

On the `/standard/programmer_un_extra` page, the shift table shows a new
**Expected attendees** column between the **Hour** and **Available seats**
columns.

- The cell displays the number of members already registered for the shift
  (`seats_reserved`).
- If at least one member is registered, a link icon (↗) appears next to the
  count. Clicking it opens a modal listing the names of all registered members.

## FTOP programmer modal

Inside the FTOP shift programmer dialog (`mywork_ftop`), the same
**Expected attendees** column is added to the shift table with identical
behaviour.

## Customising the column label

The column label "Expected attendees" is defined in the QWeb templates
`coop_memberspace_attendee.programmer_un_extra_inherit`,
`coop_memberspace_attendee.programmer_modal_inherit`, and
`coop_memberspace_attendee.mywork_ftop_inherit`.

To display a different label (e.g. a translated string), inherit those
templates in a site-specific module and replace the label with an
`xpath position="replace"` targeting the relevant `<th>` or `<p>` element.
