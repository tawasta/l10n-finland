# -*- coding: utf-8 -*-


from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def fetched_business_ids(self, parent_id, own_id=False):
        for business_id in self.env['res.partner'].search(
                [('id', '!=', own_id)]).mapped('business_id'):
            if business_id and (business_id != parent_id.business_id):
                yield business_id

    def check_duplicate_business_id(self, own_id=False):
        parent_id = self.parent_id
        if self.business_id in self.fetched_business_ids(parent_id, own_id):
            raise ValidationError(_('Business ID has to be unique!'))

    @api.onchange('business_id')
    def business_id_onchange(self):
        own_id = self._origin.id
        self.check_duplicate_business_id(own_id)

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        own_id = self.id
        self.check_duplicate_business_id(own_id)
        return res
