from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        # Set before super(): core _fields_sync() would otherwise overwrite the
        # company registry with the value of the parent's commercial partner
        defaults = self.default_get(["type", "parent_id"])
        for vals in vals_list:
            parent = self.browse(vals.get("parent_id", defaults.get("parent_id")))
            if self._check_if_invoice_address_with_its_own_company_registry(
                vals.get("type", defaults.get("type")),
                vals.get("company_registry"),
                parent,
            ):
                vals.update(is_company=True, company_type="company")
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)

        # A change in any of these can turn a partner into an invoice address
        # that has its own company registry
        trigger_fields = {
            "type",
            "company_registry",
            "is_company",
            "company_type",
        }

        if any(field in vals for field in trigger_fields):
            self._mark_invoice_addresses_as_company()
        return res

    def _mark_invoice_addresses_as_company(self):
        """Mark the invoice addresses with their own company registry as companies

        :return: the partners that were marked
        """
        matching_addresses = self.filtered(
            lambda partner: partner._should_be_marked_as_company()
        )
        # Return early, as writing even an empty recordset would
        # re-enter write() in an infinite loop
        if not matching_addresses:
            return matching_addresses

        matching_addresses.write({"is_company": True})
        return matching_addresses

    def _should_be_marked_as_company(self):
        """Return True for an individual invoice address with own company registry"""
        self.ensure_one()
        return (
            not self.is_company
            and self._check_if_invoice_address_with_its_own_company_registry(
                self.type, self.company_registry, self.parent_id
            )
        )

    @api.model
    def _check_if_invoice_address_with_its_own_company_registry(
        self, partner_type, company_registry, parent
    ):
        """Return True if the values describe an invoice address whose company
        registry differs from the parent's"""
        # A registry equal to the parent's comes from the core commercial field
        # sync (or a copy) and must not detach the address from its parent
        return (
            partner_type == "invoice"
            and bool(company_registry)
            and company_registry != parent.commercial_partner_id.company_registry
        )
