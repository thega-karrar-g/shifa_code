from odoo import api, fields, models, _


class ShifaWebRequest(models.Model):
    _name = 'sm.shifa.web.request'
    _description = "Web Request"
    _rec_name = 'service_name'

    STATES = [
        ('Received', 'Received'),
        ('Processed', 'Processed'),
    ]

    serial_no = fields.Char(string='Reference #')

    service_name = fields.Char(string='Service Name', required=True, readonly=True,
                               states={'Received': [('readonly', False)]})
    requested_by = fields.Char(string='Requested By', required=True, readonly=True,
                               states={'Received': [('readonly', False)]})
    address = fields.Char(string='Address', readonly=True, states={'Received': [('readonly', False)]})
    mobile = fields.Char(string='Mobile Number', readonly=True, states={'Received': [('readonly', False)]})
    email = fields.Char(string='Email', readonly=True, states={'Received': [('readonly', False)]})
    patient_comment = fields.Char(string='Patient Comments', readonly=True, states={'Received': [('readonly', False)]})
    call_center_comment = fields.Char(string='Call Center Comments', readonly=True,
                                      states={'Received': [('readonly', False)]})
    state = fields.Selection(STATES, string='States', readonly=True, states={'Received': [('readonly', False)]})

    def set_to_processed(self):
        return self.write({'state': 'Processed'})

    def generate_serial_no(self):
        for i in range(1,50):
            s_no = f"WR_{i:05}"
            print('serial no: ', str(s_no))


class InstantConsultancyChargeService(models.Model):
    _name = 'sm.shifa.miscellaneous.charge.service'
    _description = 'Miscellaneous Charges Service Product'
    _inherits = {
        'product.product': 'product_id',
    }
    _rec_name = "name"

    product_id = fields.Many2one('product.product', string='Related Product', required=True, ondelete='cascade',
                                 help='Product-related data of the hospital services')
    code = fields.Char(string='Code', readonly=True)

    def write(self, vals):
        res = super(InstantConsultancyChargeService, self).write(vals)
        if 'lst_price' in vals and vals['lst_price'] > 0:
            services = self.env['sm.shifa.package.service'].sudo().search([('miscellaneous_charge','=',self.id)])
            for service in services:
                service.sudo().write({"miscellaneous_price": vals['lst_price']})
                service._calculate_package_price()
                service.sudo().product.write({"lst_price": service.package_price + service.discount_amount})

        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'list_price' in vals and vals['list_price'] > 0:
            services = self.env['sm.shifa.instant.consultancy.charge'].sudo().search([('consultancy_name','=',self.name)])
            for service in services:
                service.sudo().write({"charge": vals['list_price']})

        return res

