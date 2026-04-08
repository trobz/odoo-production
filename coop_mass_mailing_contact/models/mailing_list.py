from odoo import Command, api, fields, models


class MailingList(models.Model):
    _inherit = "mailing.list"

    is_member_contact = fields.Boolean(
        default=False, help="Populate the contact from the members"
    )

    def compute_contacts(self, limit=1000):
        self.remove_contacts()
        self.add_contacts(limit)

    def remove_contacts(self):
        if not self:
            return
        sql = """
        DELETE FROM mailing_subscription
        WHERE id IN (
            SELECT ms.id
            FROM mailing_contact ct
            JOIN mailing_subscription ms
                ON ms.contact_id = ct.id
            JOIN (
                SELECT DISTINCT ON (email) id, email, is_member
                FROM res_partner
                ORDER BY email, is_member DESC NULLS LAST
            ) rp
                ON rp.email = ct.email
            WHERE rp.is_member IS FALSE
                AND ms.list_id IN %s
        )
        """
        self._cr.execute(sql, [tuple(self.ids + [-1])])

    def add_contacts(self, limit=1000):
        if not self:
            return
        sql = """
            SELECT rp.id, rp.name, rp.email
            FROM res_partner rp
            LEFT JOIN mailing_contact ct
                ON rp.email = ct.email
            WHERE ct.id IS NULL
                AND rp.email IS NOT NULL
                AND rp.is_member IS TRUE
            LIMIT %s
        """
        self._cr.execute(sql, [limit])
        datas = self._cr.fetchall()
        for data in datas:
            vals = {
                "name": data[1],
                "email": data[2],
                "is_member_contact": True,
                "subscription_ids": [],
            }
            for mailing_list in self:
                vals["subscription_ids"].append(
                    Command.create({"list_id": mailing_list.id, "opt_out": False})
                )
            self.env["mailing.contact"].create(vals)

    @api.model
    def cron_compute_contact(self, limit=1000):
        """
        F#44056 - Chaudron - Envoi en masse
        - Remove the contact which not the member anymore
        - Create new contact for a new member
        """
        mailing_lists = self.search([("is_member_contact", "=", True)])
        mailing_lists.compute_contacts(limit)
