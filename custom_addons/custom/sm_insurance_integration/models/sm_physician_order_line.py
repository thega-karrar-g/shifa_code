from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InheritPhysicianOrder(models.Model):
    """to get records line from image request ."""
    _inherit = 'sm.physician.order.line'

    authorization_request_id = fields.Many2one('sm.pre.authorization.request')
