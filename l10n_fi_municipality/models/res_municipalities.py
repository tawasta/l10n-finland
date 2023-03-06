# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResMunicipalities(models.Model):

    # 1. Private attributes
    _name = "res.municipality"
    _description = "municipalities"
    _order = "code"

    name = fields.Char(
        string="Municipality name", required=True, help="Municipality name"
    )

    code = fields.Char(string="Municipality code", help="Municipality code")

    municipality_form = fields.Char(
        string="Municipality form", help="Municipality form"
    )

    state_id = fields.Many2one(
        string="Province name", help="Province name", comodel_name="res.country.state"
    )

    state_code = fields.Char(
        string="Province code", help="Province code", related="state_id.code"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
