# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # ``shift.shift.stage_id`` now targets the new ``shift.stage`` model instead
    # of ``event.stage``. The existing column still holds legacy ``event.stage``
    # ids; clear them before the schema sync recreates the foreign key towards
    # ``shift_stage``, otherwise adding the constraint fails on orphan values.
    cr.execute("UPDATE shift_shift SET stage_id = NULL WHERE stage_id IS NOT NULL")
    _logger.info(
        "coop_shift: cleared %d legacy event.stage reference(s) on"
        " shift_shift.stage_id",
        cr.rowcount,
    )
