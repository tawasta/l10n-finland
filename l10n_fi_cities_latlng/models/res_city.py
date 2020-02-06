from odoo import fields, models


class ResCityLatLong(models.Model):
    _inherit = 'res.city'

    latitude = fields.Float(default="0.0")
    longitude = fields.Float(default="0.0")
