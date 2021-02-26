##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
{
    "name": "Finnish Invoice: Header text",
    "summary": "Add Header text to Finnish Invoice template",
    "version": "12.0.1.0.2",
    "category": "CRM",
    "website": "https://github.com/Tawasta/l10n-finland",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto-install": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "l10n_fi_invoice",
        "sale_order_header",
    ],
    "data": [
        'views/account_invoice_templates.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
