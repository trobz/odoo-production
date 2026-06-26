import logging

from odoo.tools import convert

_logger = logging.getLogger(__name__)


def force_update_data(cr, module, paths):
    for file_path in paths:
        convert.convert_file(
            cr,
            module,
            file_path,
            None,
            mode="init",
            kind="data"
        )

def migrate(cr, version):
    if not version:
        return
    force_update_data(
        cr,
        "coop_shift",
        (
            "report/report_timesheet.xml",
        )
    )
    _logger.info("Updated report timesheet")
