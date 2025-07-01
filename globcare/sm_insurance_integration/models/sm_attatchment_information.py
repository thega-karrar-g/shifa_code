from odoo import models, fields, api, _
class PreAuthorizationAttachment(models.Model):
    _name = 'sm.pre.authorization.attachment'
    _description = 'Attachment Information'

    authorization_request_id = fields.Many2one('sm.pre.authorization.request', string='Authorization Request')
    file_name = fields.Char(string='File Name')
    file_type = fields.Char(string='File Type')
    comment = fields.Text(string='Comment')
    attachment_file = fields.Binary(string='Attach File')