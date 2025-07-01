from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Partner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(index=True, translate=True)
