# Copyright 2017 Oy Tawasta OS Technologies Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, models
from odoo.exceptions import ValidationError

# Number-space specific multipliers
FINNISH_ID_DIGIT_MULTIPLIERS = [7, 9, 10, 5, 8, 4, 2]


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange(
        "company_registry",
        "country_id",
    )
    def _check_company_registry(self):
        for record in self:
            record.validate_company_registry()

    @api.onchange("company_registry", "country_id")
    def _compute_vat_from_company_registry(self):
        # When company registry is filled, autofill VAT
        for record in self:
            company_registry = record.company_registry
            if not company_registry:
                # Unset VAT
                record.vat = False
                continue

            country_code = record.country_id.code

            # Remove country code from company registry, if present
            company_registry = company_registry.replace(country_code, "")
            if record.country_id.code == "FI":
                # Reformat business id from 12345671 to 1234567-1
                if re.match("^[0-9]{8}$", company_registry):
                    record.company_registry = "{}-{}".format(
                        company_registry[:7], company_registry[7:]
                    )

                # Construct the VAT code:
                # Country code + company registry without dash
                # E.g. 1234567-1 -> FI12345671
                vat = "{}{}".format(
                    record.country_id.code,
                    company_registry.replace("-", ""),
                )
                record.vat = vat

    def _compute_company_registry_from_vat(self):
        # Compute company registry when VAT is given without company registry
        for record in self:
            country_code = record.country_id.code
            if country_code == "FI" and record.vat and not record.company_registry:
                vat = record.vat.replace(country_code, "")
                record.company_registry = "{}-{}".format(vat[0:-1], vat[-1:])

    def validate_business_code(self):
        # Deprecated. For backwards-compatibility
        self.validate_company_registry()

    def validate_company_registry(self):
        for record in self:
            if record.company_registry and record.country_id:
                # Try to find a validator function by partner country code

                # The method name should be
                # "_company_registry_validate_{lowercase_country_code}"
                # e.g. "_company_registry_validate_fi"
                validator_method_name = (
                    "_company_registry_validate_%s" % record.country_id.code.lower()
                )

                # Check if the method exists
                if hasattr(self, validator_method_name):
                    # Run the validator
                    validator_method = getattr(self, validator_method_name)
                    validator_method()

    # Finnish (FI) business code validation
    def _company_registry_validate_fi(self):
        self.ensure_one()

        company_registry = self.company_registry

        if re.match("^[0-9]{3}[.][0-9]{3}$", company_registry):
            # Registered association (rekisteröity yhdistys, ry / r.y.).
            # Format 123.456
            return True

        # Validate business id formal format
        if not re.match("^[0-9]{7}[-][0-9]{1}$", company_registry):
            msg = _("Your Company Registry is invalid. Please use format 1234567-1")
            raise ValidationError(msg)

        # The formal format is ok, check the validation number
        multipliers = FINNISH_ID_DIGIT_MULTIPLIERS
        validation_multiplier = 0  # Initial multiplier

        # business id without "-" for validation
        company_registry_number = re.sub("[^0-9]", "", company_registry)
        validation_bit = company_registry_number[7:8]

        # Test the validation bit
        for number, multiplier in zip(company_registry_number[0:7], multipliers):
            validation_multiplier += multiplier * int(number)
        modulo = validation_multiplier % 11

        # Get the final modulo
        if 2 <= modulo <= 10:
            modulo = 11 - modulo

        if int(modulo) != int(validation_bit):
            # The validation bit doesn't match
            msg = "%s %s" % (
                _("Your Company Registry validation digit is invalid."),
                _("Please check the given Company Registry."),
            )
            raise ValidationError(msg)
