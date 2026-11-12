from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def address_get(self, adr_pref=None):
        """Suggest the partner's invoice address that is a company

        This module turns invoice addresses with their own company registry
        into companies, but by default core address_get() doesn't look into children
        that are companies. Documents that take their invoice address from
        address_get() (e.g. sale orders) would then suggest the partner
        itself, even though it has an invoice address of its own.

        When the ir.config setting is enabled and the partner has exactly one invoice
        address that is a company, it is suggested as the invoice address.
        With several, there is no reliable choice and core's result is kept.
        """
        result = super().address_get(adr_pref)
        if "invoice" not in (adr_pref or []):
            return result
        if not self._is_company_invoice_address_suggestion_enabled():
            return result

        company_address = self._get_single_company_invoice_address()
        # Replace only core's fallback (the contact or the partner itself), so
        # a regular invoice address found by core or a default set by another
        # module (e.g. partner_default_invoice_address) wins, whatever the
        # module load order
        if company_address and result["invoice"] in (self.id, result.get("contact")):
            result["invoice"] = company_address.id
        return result

    @api.model
    def _is_company_invoice_address_suggestion_enabled(self):
        # sudo: address_get also runs for portal and public users (e.g. in the
        # website checkout), who can't read system parameters
        return bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "l10n_fi_company_registry_invoice_addresses_are_companies."
                "suggest_company_invoice_address"
            )
        )

    def _get_single_company_invoice_address(self):
        """Return the partner's only invoice address that is a company, or an
        empty recordset when it has none or several"""
        if len(self) != 1:
            return self.browse()
        company_addresses = self.child_ids.filtered(
            lambda child: child._is_company_invoice_address()
        )
        if len(company_addresses) != 1:
            return self.browse()
        return company_addresses

    def _is_company_invoice_address(self):
        self.ensure_one()
        return self.type == "invoice" and self.is_company

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
