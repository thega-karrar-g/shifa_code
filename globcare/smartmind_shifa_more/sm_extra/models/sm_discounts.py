import datetime

from odoo import api, fields, models, _
import string
import random
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ShifaDiscounts(models.Model):
    _name = 'sm.shifa.discounts'
    _description = "Discounts"

    STATE = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    ]
    discounts = [
        # ('Fixed', 'Fixed'),
        ('Percentage', 'Percentage'),
    ]
    state_readonly = {'Draft': [('readonly', False)], 'Active': [('readonly', False)]}

    name = fields.Char(string='Name', required=True, readonly=True, states=state_readonly)
    start_date = fields.Date(string='Start Date', required=True, readonly=True, states=state_readonly)
    exp_date = fields.Date(string='Expiration date', required=True, readonly=True, states=state_readonly)
    state = fields.Selection(STATE, string='Status', readonly=True, copy=False, help="Status of insurance", default=lambda *a: 'Draft')
    discounts_type = fields.Selection(discounts, string='Discount type', readonly=True, default=lambda *a: 'Percentage', states=state_readonly)
    percentage_type = fields.Integer(string='Percentage(%)', readonly=True, states=state_readonly)
    fixed_type = fields.Float(string='Amount(%)', readonly=True, states=state_readonly)#SR
    apply_to = fields.Text(readonly=True, states=state_readonly)
    hhc = fields.Boolean(readonly=True, states=state_readonly)
    tele = fields.Boolean(readonly=True, states=state_readonly)
    pcr = fields.Boolean(readonly=True, states=state_readonly)
    hvd = fields.Boolean(readonly=True, states=state_readonly)
    physiotherapy = fields.Boolean(readonly=True, states=state_readonly)
    customer_code = fields.Char(string="Code", readonly=True, states=state_readonly)
    sleep = fields.Boolean(readonly=True, states=state_readonly)
    caregiver = fields.Boolean(readonly=True, states=state_readonly)

    def make_active(self):
        self.state = 'Active'

    def make_expired(self):
        self.search([('state', '=', 'Active'), ('exp_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Expired'
        })

    def discount_active_action(self):
        self.search([('state', '=', 'Draft'), ('start_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Active'
        })

    # def create_unique_id(self):
    #     s = random.choices(string.digits, k=2)
    #     i = random.choices(string.ascii_letters, k=3)
    #     total = i + s
    #     return ''.join(total)
    def write(self, vals):
        vals['state'] = self._compute_start_expired_date()
        return super(ShifaDiscounts, self).write(vals)

    def _compute_start_expired_date(self):
        insurance_obj = self.env['sm.shifa.discounts']
        count_start = insurance_obj.search_count([('start_date','=', self.start_date),('start_date', '<=', fields.Date.to_string(date.today()))])
        if count_start > 0:
            count_expired = insurance_obj.search_count([('exp_date', '=', self.exp_date),('exp_date', '<=', fields.Date.to_string(date.today()))])
            if count_expired > 0:
                return 'Expired'
            else:
                return 'Active'
        else:
            return 'Draft'

    @api.model
    def create(self, vals):
        if vals['name']:
            s = random.choices(string.digits, k=2)
            i = random.choices(string.ascii_letters, k=3)
            total = i + s

            vals['customer_code'] = ''.join(total)
        return super(ShifaDiscounts, self).create(vals)
