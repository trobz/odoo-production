Once a mailing list has **Is Member Contact** enabled:

- The list is synchronized automatically every day at 20:00.
- New cooperative members (partners with `is_member = True` and a valid email)
  are added as contacts.
- Contacts whose partner is no longer a member are removed from the list.

To trigger a manual sync at any time:

1. Go to **Settings → Technical → Automation → Scheduled Actions**.
2. Find **"Mailing List: Add the contact from member"** and click **Run Manually**.
3. Open the mailing list and click the **Recipients** stat button to confirm
   the contacts have been updated.
