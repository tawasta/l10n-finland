import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def action_update_25_taxes_from_templates(self):
        # Adds / updates 25,5% taxes from account template
        # Warning! Will overwrite any manual changes to the 25,5% taxes
        self.ensure_one()

        # We are running the action for all companies, so sudo is necessary
        self = self.sudo()

        companies = self.env["res.company"].search([])
        tax_template_ids = self.env["account.tax.template"].search(
            [("name", "like", "25.5%")]
        )
        fp_templates = self.env["account.fiscal.position.template"].search(
            [("chart_template_id", "=", self.id)]
        )
        taxes_ref = {}

        for company in companies:
            # Generate 25,5% taxes
            generated_tax_res = tax_template_ids.sudo()._generate_tax(company)
            taxes_ref.update(generated_tax_res["tax_template_to_tax"])
            _logger.info(_("Added 25,5% taxes"))

            # Change default taxes, if necessary
            if company.account_sale_tax_id.amount == 24.0:
                sale_tax_25 = self.env["account.tax"].search(
                    [
                        ("name", "=", "25.5%"),
                        ("company_id", "=", company.id),
                        ("type_tax_use", "=", "sale"),
                    ]
                )
                if sale_tax_25:
                    company.account_sale_tax_id = sale_tax_25.id
                    _logger.info(_("Changed the default sales tax from 24% to 25,5%"))
            if company.account_purchase_tax_id.amount == 24.0:
                purchase_tax_25 = self.env["account.tax"].search(
                    [
                        ("name", "=", "25.5%"),
                        ("company_id", "=", company.id),
                        ("type_tax_use", "=", "purchase"),
                    ]
                )
                if purchase_tax_25:
                    company.account_purchase_tax_id = purchase_tax_25.id
                    _logger.info(
                        _("Changed the default purchase tax from 24% to 25,5%")
                    )

            # Update fiscal positions
            tax_template_vals = []

            for fp_template in fp_templates:
                # Construct a corresponding xml id for the fp
                fp_xml_id = fp_template.get_external_id()[fp_template.id].replace(
                    "l10n_fi.", "l10n_fi.{}_".format(company.id)
                )
                fp = self.env.ref(fp_xml_id, raise_if_not_found=False)
                if not fp:
                    continue

                _logger.info(
                    _(
                        "Updating '{}' tax mappings for fiscal position '{}'".format(
                            company.name, fp.name
                        )
                    )
                )

                if not fp:
                    # Can't find corresponding fiscal position by name,
                    # so it's not possible to safely add the tax mappings
                    _logger.info(
                        _(
                            "Could not find fiscal position '{}'".format(
                                fp_template.name
                            )
                        )
                    )
                    continue
                for tax in fp_template.tax_ids:
                    if (
                        "25.5%" not in tax.tax_src_id.name
                        and "25.5%" not in tax.tax_dest_id.name
                    ):
                        # Only create mappings for 25,5% taxes
                        continue

                    # Construct a corresponding xml id for the tax
                    src_id = tax.tax_src_id
                    if src_id.id in taxes_ref:
                        tax_src_id = taxes_ref[src_id.id]
                    else:
                        src_xml_id = src_id.get_external_id()[src_id.id].replace(
                            "l10n_fi.", "l10n_fi.{}_".format(company.id)
                        )
                        tax_src_rec = self.env.ref(src_xml_id)
                        if tax_src_rec._name != "account.tax":
                            tax_src_id = False
                        else:
                            # We can only refer to account.tax -records
                            tax_src_id = tax_src_rec.id

                    dest_id = tax.tax_dest_id
                    if dest_id.id in taxes_ref:
                        tax_dest_id = taxes_ref[dest_id.id]
                    else:
                        dest_xml_id = dest_id.get_external_id()[dest_id.id].replace(
                            "l10n_fi.", "l10n_fi.{}_".format(company.id)
                        )
                        tax_dest_rec = self.env.ref(dest_xml_id)
                        if tax_dest_rec._name != "account.tax":
                            tax_dest_id = False
                        else:
                            # We can only refer to account.tax -records
                            tax_dest_id = tax_dest_rec.id

                    _logger.info(
                        "Mapping tax '{}' to '{}'".format(
                            tax.tax_src_id.name, tax.tax_dest_id.name
                        )
                    )

                    if tax_src_id and tax_dest_id:
                        tax_template_vals.append(
                            (
                                tax,
                                {
                                    "tax_src_id": tax_src_id,
                                    "tax_dest_id": tax_dest_id,
                                    "position_id": fp.id,
                                },
                            )
                        )

                _logger.info(
                    _(
                        "Updated '{}' tax mappings for fiscal position '{}'".format(
                            company.name, fp.name
                        )
                    )
                )

            self._create_records_with_xmlid(
                "account.fiscal.position.tax", tax_template_vals, company
            )
