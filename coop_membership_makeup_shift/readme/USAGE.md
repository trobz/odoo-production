## Configuration

### Enable the make-up shift feature

1. Go to **Configuration → Settings**
2. In the **Memberspace** section, tick **"Show schedule a make-up shift"**
3. Click **Save**

Once enabled, the "Schedule a make-up shift" block appears on the member's
`/my/home` page alongside "Exchange of services".

---

## Member Workflow

### Eligibility conditions

A member is eligible to register a make-up shift when **all three** conditions
are met on their `res.partner` record:

| Field | Required value |
|-------|---------------|
| `shift_type` | `standard` |
| `cooperative_state` | `alert`, `suspended`, or `delay` |
| `final_standard_point` | < 0 |

### Registering a make-up shift

1. Log in to the website as a standard member
2. Go to **My participation** (`/my/home`) → click **"Schedule"** in the
   "Schedule a make-up shift" block, or navigate directly to
   `/standard/programmer_makeup`
3. A table lists upcoming available shifts:
   - Shifts starting **from tomorrow** onwards
   - Not belonging to the member's own shift template
   - With at least one **standard ticket** that has available seats
   - Not already registered by the member
   - Not cancelled
4. Click the **+** icon on the desired shift:
   - **Eligible member** → confirmation modal opens, shows the date and hour
   - **Ineligible member** → warning modal opens explaining the current status
5. Click **✓** to confirm → registration is created with `is_makeup = True`;
   the seat count decreases by 1 and the icon turns grey

### Row colour coding

Rows inherit the colour logic from `coop_memberspace`:

| Colour | Meaning |
|--------|---------|
| Red | Shift starts within 3 days |
| Orange | > 75 % of seats still available |
| Yellow | 50 – 75 % of seats available |
| Beige | < 50 % of seats available |

---

## Back-office verification

After a member registers a make-up shift, verify the result under
**Shifts → Registrations**:

| Field | Expected value |
|-------|---------------|
| `partner_id` | The member who registered |
| `shift_id` | The selected shift |
| `shift_ticket_id.shift_type` | `standard` |
| `is_makeup` | `True` |
| `state` | `draft` |
| `related_extension_id` | empty |

---

## Troubleshooting

### The make-up shift table is empty

1. Check that at least one shift from a **different template** than the member's
   own exists in the future with `seats_max > 0` on its standard ticket
2. Confirm in the Odoo shell:

```python
partner = env['res.partner'].browse(<id>)
print(partner.check_makeup_shift())          # must be True
print(partner.tmpl_reg_line_ids.filtered(lambda r: r.is_current))  # must be non-empty
```

### The "Schedule a make-up shift" block does not appear on /my/home

Check that the company setting is enabled:

```python
env.user.company_id.shift_makeup  # must be True
```
