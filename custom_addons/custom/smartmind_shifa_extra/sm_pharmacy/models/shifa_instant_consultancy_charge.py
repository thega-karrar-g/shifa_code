from odoo import models, fields, api


class InstantConsultancyCharge(models.Model):
    _name = 'sm.shifa.instant.consultancy.charge'
    _description = 'Instant Consultancy Charge'

    consultancy_name = fields.Char(string='Consultancy Name', readonly=True)
    code = fields.Char(string='Code', readonly=True)
    cost = fields.Float(string='Cost', default=0)
    charge = fields.Float(string='Charge')
    product_id = fields.Many2one('product.product')
    

    def write(self, vals):
        model_name = 'sm.shifa.miscellaneous.charge.service'
        service_charge = super(InstantConsultancyCharge, self).write(vals)
        for rec in self:
            if rec.charge or rec.charge == 0:
                charge_service_count = self.env[model_name].sudo().search_count([('name', '=', rec.consultancy_name)])
                if charge_service_count > 0:
                    charge_service = self.env[model_name].sudo().search([('name', '=', rec.consultancy_name)], limit=1)
                    charge_service.write({
                        'standard_price': rec.cost,
                        'list_price': rec.charge,
                    })
                else:
                    self.env['sm.shifa.miscellaneous.charge.service'].create({
                        'name': rec.consultancy_name,
                        'type': 'service',
                        'standard_price': rec.cost,
                        'list_price': rec.charge,
                        'code': rec.code,
                    })

            return service_charge

