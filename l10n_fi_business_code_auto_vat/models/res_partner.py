from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("business_code", "country_id")
    def onchange_business_code_update_vat(self):
        for record in self:
            if record.country_id and record.country_id.code in ["FI", "SE"]:

                if record.business_code and not record.vat:
                    # Construct the VAT code:
                    # Country code + business id without dash
                    vat = "{}{}".format(
                        record.country_id.code,
                        record.business_code.replace("-", ""),
                    )

                    record.vat = vat
                elif record.vat and not record.business_code:
                    # This is for create and write
                    vat = record.vat
                    record.business_code = "{}-{}".format(vat[2:-1], vat[-1:])

    def write(self, vals):
        res = super().write(vals)
        if vals.get("vat") or vals.get("business_code"):
            self.onchange_business_code_update_vat()

        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)

        if vals.get("vat") or vals.get("business_code"):
            res.onchange_business_code_update_vat()

        return res
