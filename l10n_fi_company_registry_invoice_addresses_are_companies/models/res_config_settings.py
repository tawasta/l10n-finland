from odoo import _, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def action_mark_invoice_addresses_as_company(self):
        """
        Mass update existing invoice addresses to be companies
        """
        candidates = self.env["res.partner"].search(
            [
                ("type", "=", "invoice"),
                ("is_company", "=", False),
                ("company_registry", "!=", False),
            ]
        )
        marked = candidates._mark_invoice_addresses_as_company()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": _(
                    "Invoice addresses marked as companies: %(count)s",
                    count=len(marked),
                ),
                "type": "success",
                "sticky": False,
            },
        }
