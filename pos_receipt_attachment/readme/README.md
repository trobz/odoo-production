# Point of Sale - Attach Receipt to Backend

## Overview

- The POS Receipt screen generates a receipt image.
- The image is sent to the backend through an RPC call to `pos.order.add_image_receipt(uuid, data)`.
- If the order already exists, the image is stored on the order (`pos.order.image_receipt`, stored as an attachment).
- If the order does not exist yet, an orphan `ir.attachment` is created and later linked by a cron job.

## Scheduled Actions

- **Pos Order: Update image receipt attachment**
  - Method: `pos.order.cron_update_image_receipt()`
  - Links orphan attachments to the matching `pos.order` by UUID.

## Dependencies

- `point_of_sale`
- `pos_ticket_send_by_mail`

## Usage

- Open a POS session and complete an order.
- When the Receipt screen is displayed, the receipt image is generated and sent automatically.
- In the backend, open the created POS order; the receipt image is available in the `image_receipt` attachment field.

## Notes

- If the backend is temporarily unreachable, the POS UI stores the receipt image in local pending storage and retries on next load.
