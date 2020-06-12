##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2020- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Finnish Invoice - Report text by country group",
    "summary": "Get finnish invoice report text from country groups setting",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/Tawasta/account-invoicing",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["l10n_fi_invoice", "l10n_fi_country_groups", "account_invoice_country_group_text"],
    "data": ["views/country_group.xml", "report/finnish_invoice.xml"],
}
