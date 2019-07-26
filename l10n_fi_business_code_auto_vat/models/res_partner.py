# -*- coding: utf-8 -*-

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('business_id', 'country_id')
    def onchange_business_id_update_vat(self):
        for record in self:
            if record.business_id and record.country_id and \
                    record.country_id.code in ['FI', 'SE']:
                # Construct the VAT code:
                # Country code + business id without dash
                vat = '%s%s' % (
                    record.country_id.code,
                    record.business_id.replace('-', '')
                )

                record.vat = vat
