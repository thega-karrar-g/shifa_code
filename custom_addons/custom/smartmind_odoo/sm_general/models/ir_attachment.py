
import uuid

from odoo import api, fields, models, tools


class Attachment(models.Model):

    _inherit = "ir.attachment"

    access_token = fields.Char('Token', readonly=True)

    @api.model
    def create(self, vals):
        res = super(Attachment, self).create(vals)
        res.access_token = uuid.uuid4()
        return res
    
# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
