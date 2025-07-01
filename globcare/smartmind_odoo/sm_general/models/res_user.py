from odoo import models, fields, api


class ExternalSupervisorResUser(models.Model):
    _inherit = 'res.users'

    external_facility = fields.Many2one('sm.shifa.external.facility.contract')
