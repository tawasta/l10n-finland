from odoo import models, fields


class ResLocationCity(models.Model):
    _name = "res.location_city"

    name = fields.Char(string="Name")
    display_name = fields.Char(string="Display Name")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    state_id = fields.Many2one(comodel_name="res.country.state", string="State")
