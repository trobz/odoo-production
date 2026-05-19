Email Alias feature

- Each team/template will have 2 email alias:
  - 1 for the Coordinators of the team, naming convention of alias for
    Coordinators: coordos.\[week\]\[day\]\[hour\]@\[domain\]
  - 1 for the Members of the Team (including the Coordinators): naming
    convention of alias for Members:
    service.\[week\]\[day\]\[hour\]@\[domain\]
- Alias domain is configured by parameter object:
  - with key: mail.catchall.domain.
  - value: your email domain (e.g: cooplaloue.fr)

When installing module, there is a script to create email alias
automatically for each template, so, mail.catchall.domain must exist
before installing coop_memberspace module.

- There are 2 main objects to store email alias for each team:
  - memberspace_alias: store all alias of team (access via Member config
    menu: Members \> Configuration \> Memberspace Alias)
  - memberspace_conversation: store all conversation of each topic
    (access via Member config menu: Members \> Configuration \>
    Memberspace Conversation). Every time a new email which sent to
    specific alias, a new conversation will be created, then after that,
    all reply of the conversation will be stored within this
    conversation.

How Alias works?

Any mail sent to your domain, that doesn't have a defined mailbox, will
be sent to your catchall email. Application fetches the emails with a
cron (using the module fetchmail) and dispatches them to corresponding
virtual mail address (alias)

Note: Make sure you set your created mailbox of Incoming Mail Server as
the catch-all.

## JavaScript Widget Extensibility

All public widgets in this module are exported with `export default`,
allowing other modules to import and extend them.

The following widgets and utilities are available for inheritance:

| File | Export |
|---|---|
| `static/src/js/exchange_shift.esm.js` | `publicWidget.registry.exchange_shift` |
| `static/src/js/my_profile.esm.js` | `publicWidget.registry.my_profile` |
| `static/src/js/mywork_ftop.esm.js` | `publicWidget.registry.mywork_ftop` |
| `static/src/js/programmer_un_extra.esm.js` | `publicWidget.registry.programmer_un_extra` |
| `static/src/js/programmer_une_vacation.esm.js` | `publicWidget.registry.programmer_une_vacation` |
| `static/src/js/statistics.esm.js` | `publicWidget.registry.statistics` |
| `static/src/js/style.esm.js` | `showErrorMsg` (utility function) |

### Extending a widget from another module

Use `include()` to patch a widget in-place (all instances are affected):

```js
import ProgrammerUneVacation from "@coop_memberspace/static/src/js/programmer_une_vacation.esm";

ProgrammerUneVacation.include({
    // Override the method that builds each shift row HTML
    parse_body_ftop_programmer(shift) {
        // Add custom logic before/after the base implementation
        const baseHtml = this._super(shift);
        return baseHtml; // or return a customized version
    },

    // Hook called after a shift is successfully created
    post_create_shift() {
        this._super();
        // e.g. refresh a custom counter or send an analytics event
    },
});
```

Use `extend()` to create a new widget class (original is unchanged):

```js
import ProgrammerUneVacation from "@coop_memberspace/static/src/js/programmer_une_vacation.esm";
import { registry } from "@web/core/registry";

publicWidget.registry.my_custom_programmer = ProgrammerUneVacation.extend({
    selector: ".my-custom-programmer",
    // Override or add methods here
});
```

### Reusing the shared utility

```js
import { showErrorMsg } from "@coop_memberspace/static/src/js/style.esm";

// Displays a dismissible Bootstrap warning flash at the top of the page
showErrorMsg("Something went wrong.");
```
