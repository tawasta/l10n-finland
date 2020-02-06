from odoo import fields, models


class ResCountryStateLatLong(models.Model):

    _inherit = 'res.country.state'

    latitude = fields.Float(default="0.0")
    longitude = fields.Float(default="0.0")
