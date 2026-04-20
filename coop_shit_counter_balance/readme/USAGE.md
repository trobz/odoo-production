The balancing runs automatically every day via a scheduled action.

To trigger it manually:

1. Go to **Settings → Technical → Automation → Scheduled Actions**
2. Find *"Balance negative ABCD counter when vacation counter positive"*
3. Click **Run Manually**

The action will find all members where:

- Standard counter (`display_std_points`) is negative
- FTOP/vacation counter (`display_ftop_points`) is positive

For each such member, it creates two counter events:

- A positive **Standard** event to reduce the deficit
- A negative **FTOP** event to consume the vacation surplus

The transferred amount equals `min(|std_points|, ftop_points)`, capped at 1000 members per run.
