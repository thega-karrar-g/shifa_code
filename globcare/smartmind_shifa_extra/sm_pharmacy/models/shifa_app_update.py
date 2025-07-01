from odoo import models, fields, api


class InstantConsultancyCharge(models.Model):
    _name = 'sm.shifa.app.update'
    _description = 'App Update'
    _rec_name = "app_update"

    app_update = fields.Char(string='App Update', readonly=True)
    code = fields.Char(string='Code', readonly=True)
    version = fields.Char(string='Version')

    @api.model
    def create(self, vals):
        return super(InstantConsultancyCharge, self).create(vals)
