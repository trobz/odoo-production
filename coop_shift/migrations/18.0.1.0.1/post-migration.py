from odoo import SUPERUSER_ID, api
from odoo.tools import convert

def migrate(cr, version):
    # Hard reset report timesheet
    env = api.Environment(cr, SUPERUSER_ID, {})
    convert.convert_file(
        env,
        "coop_shift",
        "report/report_timesheet.xml",
        None,
        mode="init",
        kind="data"
    )
