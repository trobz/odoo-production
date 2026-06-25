import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Create missing POS Picking Sequence...")

    warehouses = env["stock.warehouse"].sudo().search([("pos_type_id", "!=", False)])
    for warehouse in warehouses:
        pos_type = warehouse.pos_type_id
        if pos_type.sequence_id:
            continue

        sequence_code = pos_type.sequence_code
        picking = (
            env["stock.picking"]
            .sudo()
            .search(
                [("picking_type_id", "=", pos_type.id)],
                order="name desc",
                limit=1,
            )
        )

        if picking:
            try:
                max_sequence = int(picking.name.removeprefix(sequence_code))
            except ValueError:
                _logger.error(
                    "Cannot extract sequence number from "
                    "picking name '%s' with prefix '%s'. "
                    "No update for Operation Type '%s'",
                    picking.name,
                    sequence_code,
                    pos_type.name,
                )
                continue
        else:
            max_sequence = 0

        sequence_vals = warehouse._get_sequence_values()["pos_type_id"]
        sequence_vals["number_next_actual"] = max_sequence + 2
        sequence = env["ir.sequence"].sudo().create(sequence_vals)
        pos_type.write({"sequence_id": sequence.id})
        _logger.info(
            "Updated Operation Type '%s' with sequence_id %s",
            pos_type.name,
            sequence.id,
        )
