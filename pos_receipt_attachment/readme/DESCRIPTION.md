This module captures the POS receipt as an image from the POS UI and stores it on the corresponding POS order in the backend as an attachment.

If the order is not yet created in the backend when the receipt image is sent, the module creates an orphan `ir.attachment` and a scheduled action later links it to the matching `pos.order` using the order UUID.
