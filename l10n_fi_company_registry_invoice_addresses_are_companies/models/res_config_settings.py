from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    suggest_company_invoice_address = fields.Boolean(
        config_parameter="l10n_fi_company_registry_invoice_addresses_are_companies.suggest_company_invoice_address"
    )

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
