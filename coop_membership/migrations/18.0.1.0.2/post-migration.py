# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


# The DB copy of the welcome_email template (noupdate="1") had drifted and
# contained an invalid ``auth_login`` reference copied from the auth_signup
# template, raising ``KeyError: 'auth_login'`` when the cron rendered it.
# Because of noupdate="1", a module upgrade never overwrites the body, so we
# restore the clean body_html here for both languages. Content is kept in sync
# with data/email_template_data.xml (en_US) and i18n/fr.po (fr_FR).

WELCOME_EMAIL_BODY_EN = (
    "\n"  # noqa: E501
    '<p>Hello <span t-esc="object.name"/>,</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    '<p>Your subscription to <span t-esc="object.company_id.name"/> has been registered. Welcome !</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    "<t t-if=\"object.shift_type == 'standard'\">\n"  # noqa: E501
    '<p>Your member number is <span t-esc="object.barcode_base"/> and you have been registered on the niche <span t-esc="object.current_template_name"/>.</p>\n'  # noqa: E501
    "</t>\n"  # noqa: E501
    "<t t-if=\"object.shift_type == 'ftop'\">\n"  # noqa: E501
    '<p>Your membership number is <span t-esc="object.barcode_base"/> and you have been enrolled in the steering wheel team. You will find attached a document which explains the functioning of this team as well as a calendar which indicates the settlement dates.</p>\n'  # noqa: E501
    "</t>\n"  # noqa: E501
    "<p>You will receive a reminder a few days before your next service. <br/>\n"  # noqa: E501
    "You can now come and discover the store and do your shopping, upon presentation of an identity document.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    '<p>We invite you to connect to <a t-att-href="object.company_id.website or \'\'" style="background-color:transparent;text-decoration-thickness:auto;color:rgb(124, 123, 173);"> The Members Area </a> (in attachment, the procedure to activate it). You will find there a lot of information, in particular your next services, and a forum which will allow you to communicate between members. The current version of the site will evolve and new functionalities will be added in the coming months. A team of volunteer members works to enrich this space to make it useful and convivial.</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    "<p>Access to the store is then on presentation of the cooperator badge. To obtain your badge, you must first come to a photo session organized either at the store or during the general meetings of La Louve. The photo sessions are announced on the Members Area and at the store. As with the Members' Area, the making of badges is carried out by volunteers and requires several stages which can take several days. The complete procedure is described in the Members Area forum (FAQ section). As soon as your badge has been printed, you can collect it at the supermarket reception.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    "<p>You will find attached a procedure allowing you to activate your personal space.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    "<p>Regards,<br/>\n"  # noqa: E501
    "Tom Boothe</p>\n"  # noqa: E501
    "<br/>\n"  # noqa: E501
    "<br/>\n"  # noqa: E501
)

WELCOME_EMAIL_BODY_FR = (
    "\n"  # noqa: E501
    '<p>Bonjour <span t-esc="object.name"/>,</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    '<p>Votre souscription à <span t-esc="object.company_id.name"/> a bien été enregistrée. Bienvenue !</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    "<t t-if=\"object.shift_type == 'standard'\">\n"  # noqa: E501
    '<p>Votre numéro de membre est <span t-esc="object.barcode_base"/> et vous avez été inscrit.e sur le créneau <span t-esc="object.current_template_name"/>.</p>\n'  # noqa: E501
    "</t>\n"  # noqa: E501
    "<t t-if=\"object.shift_type == 'ftop'\">\n"  # noqa: E501
    '<p>Votre numéro de membre est <span t-esc="object.barcode_base"/> et vous avez été inscrit.e dans l’équipe volante. Vous trouverez en pièce jointe un document expliquant le fonctionnement de cette équipe ainsi qu’un calendrier indiquant les dates de décompte.</p>\n'  # noqa: E501
    "</t>\n"  # noqa: E501
    "<p>Vous recevrez un rappel quelques jours avant votre prochain service. <br/>\n"  # noqa: E501
    "Vous pouvez désormais venir découvrir le magasin et faire vos courses, sur présentation d’une pièce d’identité.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    '<p>Nous vous invitons à vous connecter à <a t-att-href="object.company_id.website or \'\'" style="background-color:transparent;text-decoration-thickness:auto;color:rgb(124, 123, 173);"> l’Espace Membres </a> (la procédure d’activation est en pièce jointe). Vous y trouverez de nombreuses informations, notamment vos prochains services, ainsi qu’un forum qui vous permettra d’échanger entre membres. La version actuelle du site continuera d’évoluer et de nouvelles fonctionnalités seront ajoutées dans les prochains mois. Une équipe de membres bénévoles travaille à enrichir cet espace pour le rendre utile et convivial.</p>\n'  # noqa: E501
    "\n"  # noqa: E501
    "<p>L’accès au magasin se fait ensuite sur présentation du badge coopérateur. Pour obtenir votre badge, vous devez d’abord venir à une séance photo organisée soit au magasin, soit pendant les réunions générales de La Louve. Les séances photo sont annoncées sur l’Espace Membres et au magasin. Comme pour l’Espace Membres, la fabrication des badges est réalisée par des bénévoles et nécessite plusieurs étapes pouvant prendre plusieurs jours. La procédure complète est décrite dans le forum de l’Espace Membres (rubrique FAQ). Dès que votre badge est imprimé, vous pouvez le récupérer à l’accueil du supermarché.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    "<p>Vous trouverez en pièce jointe une procédure vous permettant d’activer votre espace personnel.</p>\n"  # noqa: E501
    "\n"  # noqa: E501
    "<p>Cordialement,<br/>\n"  # noqa: E501
    "Tom Boothe</p>\n"  # noqa: E501
    "<br/>\n"  # noqa: E501
    "<br/>\n"  # noqa: E501
)


def migrate(cr, version):
    """Restore the welcome_email template body corrupted with 'auth_login'."""
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    template = env.ref("coop_membership.welcome_email", raise_if_not_found=False)
    if not template:
        _logger.info("welcome_email template not found, skipping body reset")
        return

    template.with_context(lang="en_US").write({"body_html": WELCOME_EMAIL_BODY_EN})
    template.with_context(lang="fr_FR").write({"body_html": WELCOME_EMAIL_BODY_FR})
    _logger.info(
        "Reset welcome_email (id=%s) body_html for en_US and fr_FR", template.id
    )
