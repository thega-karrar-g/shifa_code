import datetime

from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ShifaInsurance(models.Model):
    _name = 'sm.shifa.insurance'
    _description = "Insurances"

    _inherits = {
        'res.partner': 'partner_id',
    }

    STATE = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    ]

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')
    ref = fields.Char('Reference', index=True, copy=False)
    # name = fields.Char(string='Company Name')
    name_ar = fields.Char(string='Company Name (AR)')
    start_date = fields.Date(string='Start Date', required=True)
    exp_date = fields.Date(string='Expiration date', required=True)
    state = fields.Selection(STATE, string='Status', readonly=True, copy=False, help="Status of insurance", default=lambda *a: 'Draft')
    contract_document = fields.Binary(string='Contract Document')
    comment = fields.Text(string='Comment')
    logo = fields.Binary(string='Logo')

    @api.model
    def create(self, vals):
        # vals['company_type'] = 'regular'
        vals['state'] = self._compute_start_expired_date()
        vals['ref'] = self.env['ir.sequence'].next_by_code('sm.shifa.insurance')
        return super(ShifaInsurance, self).create(vals)

    def write(self, vals):
        vals['state'] = self._compute_start_expired_date()
        print(self.state)
        return super(ShifaInsurance, self).write(vals)

    def _compute_start_expired_date(self):
        insurance_obj = self.env['sm.shifa.insurance']
        count_start = insurance_obj.search_count([('start_date','=', self.start_date),('start_date', '<=', fields.Date.to_string(date.today()))])
        print(count_start)
        if count_start > 0:
            count_expired = insurance_obj.search_count([('exp_date','=', self.exp_date),('exp_date', '<=', fields.Date.to_string(date.today()))])
            if count_expired > 0:
                return 'Expired'
            else:
                return 'Active'
        else:
            return 'Draft'

    # @api.model
    # def create(self, vals):
    #     vals["is_insurance_company"] = True
    #     insurance = super(ShifaInsurance, self).create(vals)
    #     return insurance
    #
    # @api.depends('name', 'ins_no')
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         name = self.name
    #         if self.ins_no:
    #             name = "[" + self.ins_no + '] ' + name
    #         res += [(record.id, name)]
    #     return res
    #

    @api.constrains('start_date', 'exp_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.exp_date and c.start_date > c.exp_date):
            raise ValidationError(_('Contract start date must be earlier than contract end date.'))
        # if self.filtered(lambda c: fields.Date.to_string(c.start_date) < fields.Date.to_string(date.today())):
        #     raise ValidationError(_('Contract start date must be after today date.'))

    def make_active(self):
        return self.write({'state': 'Active'})

    def make_expired(self):
        print(1)
        self.search([('state', '=', 'Active'), ('exp_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Expired'
        })

    def insurance_active(self):
        print(self.state)
        self.search([('state', '=', 'Draft'), ('start_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Active'
        })
        # print(self.state)

    # # Preventing deletion of a insurance details which is not in draft state
    # def unlink(self):
    #     for insurance in self.filtered(lambda insurance: insurance.state not in ['Draft']):
    #         raise UserError(_('You can not delete active or expired insurance information from the system !!'))
    #     return super(ShifaInsurance, self).unlink()