from odoo import fields, models


class FactoringContract(models.Model):
    _inherit = "factoring.contract"
    _description = "Factoring Contract"
    _rec_name = "name"

    identifier_in_payment_reference = fields.Boolean(
        string="Identifier in Payment Reference",
        help="Indicates whether the factoring agreement identifier "
        "should be prefixed to the payment reference.",
    )
