# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Since v14.0, res.partner.barcode is company_dependent and stored as
    # jsonb with format {"<company_id>": "<value>"}.
    # Old data may contain plain jsonb strings (e.g. "0420000050001") that
    # must be converted to objects before Odoo reads them.
    cr.execute(
        """
        UPDATE res_partner
        SET barcode = json_build_object(
            COALESCE(company_id::text, '1'),
            barcode#>>'{}'
        )::jsonb
        WHERE barcode IS NOT NULL
          AND jsonb_typeof(barcode) = 'string'
        """
    )
    _logger.info(
        "Migrated %d res.partner barcode values to company-dependent jsonb format",
        cr.rowcount,
    )
