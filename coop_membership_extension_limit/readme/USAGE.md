This module limits the number of extensions a member can receive when they are in certain cooperative states (suspended, alerted, or delayed).

## Configuration

1. Go to **Settings > General Settings** and scroll to the Membership section
2. Enable "Member Extension Limit" to activate the feature
3. Set the maximum number of extensions allowed (default: 6)
4. Select the extension types to which the limit applies

## How It Works

- When a member in alert, suspended, or delay state receives an extension, the system counts the consecutive extensions
- Once the limit is reached, no more extensions can be granted until make-up sessions are completed
- When a member reaches one extension before the limit, a warning email is automatically sent

## Email Notifications

The module includes an email template that notifies members when they are approaching their extension limit.
