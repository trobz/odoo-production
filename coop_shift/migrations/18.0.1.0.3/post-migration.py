# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from ast import literal_eval

_logger = logging.getLogger(__name__)

# Matches the repr of a Command IntEnum member, e.g. "<Command.SET: 6>", and
# captures its integer value so it can be substituted back in.
COMMAND_REPR_RE = re.compile(r"<Command\.\w+:\s*(\d+)>")


def migrate(cr, version):
    # Before this version, shift.template.write stored ``updated_fields`` with
    # ``str(vals)``. In Odoo 18 x2many commands are ``Command`` IntEnum members,
    # so the stored string contains their repr (e.g. "<Command.SET: 6>") which
    # is not valid Python and crashes ``safe_eval`` in the update shifts wizard.
    # Salvage the affected rows by converting the enum repr back to a plain int.
    cr.execute(
        """
        SELECT id, updated_fields
        FROM shift_template
        WHERE updated_fields LIKE '%<Command.%'
        """
    )
    rows = cr.fetchall()

    fixed, cleared = 0, 0
    for template_id, updated_fields in rows:
        repaired = COMMAND_REPR_RE.sub(r"\1", updated_fields)
        try:
            # Make sure the repaired value is parseable; otherwise reset it so
            # the wizard stops crashing on this template.
            literal_eval(repaired)
        except (ValueError, SyntaxError):
            repaired = ""
            cleared += 1
        else:
            fixed += 1
        cr.execute(
            "UPDATE shift_template SET updated_fields = %s WHERE id = %s",
            (repaired, template_id),
        )

    _logger.info(
        "coop_shift: repaired %d and cleared %d corrupted updated_fields values",
        fixed,
        cleared,
    )
