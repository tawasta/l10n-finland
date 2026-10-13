from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def compute_payment_reference_finnish(self, number):
        if (
            self.factoring_contract_id
            and self.factoring_contract_id.identifier
            and self.factoring_contract_id.identifier_in_payment_reference
        ):
            identifier = self.factoring_contract_id.identifier
            number = f"{identifier.ljust(6, '0')}{number}"

        return super().compute_payment_reference_finnish(number)
