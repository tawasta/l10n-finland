# -*- coding: utf-8 -*-


from odoo import api, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def fetched_matched_partners(self, id_family, business_id):
        """Fetch partners outside id_family that have same business_id as
        selected partner"""

        matched_partners = self.env['res.partner'].search([
            ('id', 'not in', id_family),
            ('is_company', '=', True),
            ('business_id', '=', business_id)
        ])

        return matched_partners

    def check_duplicate_business_id(self, own_id):
        """Raises ValidationError if Business ID exists on partners
        outside of id_family-partners"""

        address_ids = own_id and (self.address_ids
                                  and self.address_ids.ids) or []
        own_id = own_id and [own_id] or []
        parent_id = self.parent_id and [self.parent_id.id] or []
        id_family = address_ids + own_id + parent_id

        business_id = self.business_id

        if business_id and len(self.fetched_matched_partners(
                id_family, business_id)) > 0:
            error = _('Business ID has to be unique!')
            raise ValidationError(error)

    @api.constrains('business_id')
    def business_id_constrains(self):
        """This method is used when business_id-field has been modified and the
        user is trying to save changes"""

        _logger.info("Triggered res.partner business_id_constrains-method")
        # Check if (self.business_id == False) is true, which would fetch
        # id_numbers-recordset with missing missing value due to setting
        # self.business_id to False
        own_id_number_records_names = self.get_number_ids(self.id).\
            mapped('name')

        # If self.business_id exists, then a corresponding value also exists in
        # the list own_id_number_records_names
        if self.business_id in own_id_number_records_names:
            own_id = self.id
            self.check_duplicate_business_id(own_id)

    def get_number_ids(self, partner_id):
        """Fetches id_numbers for partner"""

        id_number_recs = self.env['res.partner.id_number'].search([
            ('partner_id', '=', partner_id)
        ])

        return id_number_recs

    @api.onchange('business_id')
    def business_id_onchange(self):
        """Changing business_id-field's value will trigger this method and
        business_id will be checked for duplicates"""

        _logger.info("Triggered res.partner business_id_onchange-method")
        own_id = self._origin.id
        self.check_duplicate_business_id(own_id)
