from odoo import SUPERUSER_ID, api


def init_tax25_data(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    chart_templates = env["account.chart.template"].search([])

    for chart_template in chart_templates:
        chart_template.action_update_25_taxes_from_templates()
