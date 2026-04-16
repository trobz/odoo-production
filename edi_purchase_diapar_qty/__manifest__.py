##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "EDI Purchase Diapar Quantity",
    "summary": "Customizw EDI Purchase Diapart Quantity",
    "version": "18.0.1.0.0",
    "category": "web",
    "author": "Trobz, La Louve",
    "license": "LGPL-3",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "edi_purchase_diapar_oca",
        "purchase_package_qty",
        "coop_purchase",
    ],
    "installable": True,
    "auto_install": True,
}
