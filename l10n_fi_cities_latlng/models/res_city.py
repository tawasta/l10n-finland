from odoo import fields, models


class ResCityLatLong(models.Model):
    _inherit = "res.location_city"

    latitude = fields.Float(default="0.0")
    longitude = fields.Float(default="0.0")
