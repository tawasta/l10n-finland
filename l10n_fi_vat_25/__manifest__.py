##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2024- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
##############################################################################
{
    "name": "Finnish Localization: Add 25.5% tax",
    "summary": "Adds 25.5% tax and fiscal position mappings",
    "version": "14.0.1.0.0",
    "category": "Accounting/Localizations/Account Charts",
    "website": "https://gitlab.com/tawasta/odoo/l10n-finland",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["l10n_fi"],
    "post_init_hook": "init_tax25_data",
    "data": [
        "data/account_tax_group_data.xml",
        "data/account_tax_report_line.xml",
        "data/account_tax_template_data.xml",
        "data/account_fiscal_position_template_data.xml",
    ],
}
