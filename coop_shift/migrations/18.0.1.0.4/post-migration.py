# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # A negative ``seats_max`` is invalid data: the ticket is treated as
    # "limited" (seats_max != 0) while its available seats compute negative, so
    # ``shift.ticket._check_seats_availability`` raises "not enough seats" and
    # breaks the "Create of Shifts from Templates" cron (and any write on the
    # related shift/registration). FTOP ("Volant") tickets in particular are
    # meant to be unlimited, i.e. ``seats_max = 0``. Normalize every negative
    # value back to 0 (unlimited) on both the template tickets and the already
    # generated shift tickets.
    cr.execute("UPDATE shift_template_ticket SET seats_max = 0 WHERE seats_max < 0")
    _logger.info(
        "coop_shift: reset %d negative seats_max value(s) to 0 on"
        " shift_template_ticket",
        cr.rowcount,
    )
    cr.execute("UPDATE shift_ticket SET seats_max = 0 WHERE seats_max < 0")
    _logger.info(
        "coop_shift: reset %d negative seats_max value(s) to 0 on shift_ticket",
        cr.rowcount,
    )
