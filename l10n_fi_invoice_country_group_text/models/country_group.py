from odoo import fields, models


class CountryGroup(models.Model):

    _inherit = "res.country.group"

    finnish_invoice_text = fields.Text(
        string="Finnish Invoice Text",
        help="Text to be added on finnish invoices going to customers in this "
        + "country group.",
    )
