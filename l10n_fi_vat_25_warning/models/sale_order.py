import logging
from datetime import date

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    incorrect_tax_warning = fields.Boolean(
        string="Incorrect tax",
        help="Technical field for showing a warning, if incorrect tax is possibly used",
        compute="_compute_incorrect_tax_warning",
    )

    def _compute_incorrect_tax_warning(self):
        # Compute if invoice should use a different tax %
        cutoff_date = date(2024, 9, 1)
        for record in self:
            delivery_date = record._get_delivery_date()
            taxes = record.order_line.tax_id.mapped("amount")

            if not delivery_date:
                incorrect_tax_warning = False
            elif delivery_date < cutoff_date:
                # Should use 24% tax
                if 25.5 in taxes:
                    incorrect_tax_warning = True
                else:
                    incorrect_tax_warning = False
            else:
                # Should use 25,5% tax
                if 24.0 in taxes:
                    incorrect_tax_warning = True
                else:
                    incorrect_tax_warning = False

            record.incorrect_tax_warning = incorrect_tax_warning

    def _get_delivery_date(self):
        # A helper for overriding delivery date
        self.ensure_one()

        if hasattr(self, "picking_ids") and self.picking_ids:
            delivery_date = self.picking_ids.sorted("scheduled_date", reverse=True)[
                0
            ].scheduled_date.date()
        elif self.commitment_date:
            delivery_date = self.commitment_date.date()
        elif self.date_order:
            delivery_date = self.date_order.date()
        else:
            # date_order is mandatory, so this should never happen
            delivery_date = fields.Date.today()

        return delivery_date
