from odoo import api, models


class ResPartnerOperatorEinvoice(models.Model):
    _inherit = "res.partner.operator.einvoice"

    @api.depends("identifier", "name")
    def _compute_display_name(self):
        """
        Safe override of _compute_display_name to prevent TypeError
        if 'identifier' or 'name' is None during record creation.
        """
        for operator in self:
            identifier = operator.identifier or ""
            name = operator.name or ""
            operator.display_name = f"{identifier} - {name}".strip(" -")
