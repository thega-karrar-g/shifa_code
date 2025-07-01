import random
import string
from datetime import date
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class PharmacyChain(models.Model):
    _name = 'sm.shifa.pharmacy.chain'
    _description = "Pharmacy Chain"

    _inherits = {
        'res.partner': 'partner_id',
    }
    STATE = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    ]
    # test
    def _pharmacies_count(self):
        pharmacies_obj = self.env['sm.shifa.pharmacies']
        for phar in self:
            domain = [('institution', '=', phar.id)]
            pharmacies_ids = pharmacies_obj.search(domain)
            pharmacies = pharmacies_obj.browse(pharmacies_ids)
            ph_count = 0
            for ph_id in pharmacies:
                ph_count+=1
            phar.pharmacies_count = ph_count
        return True
    def open_pharmacies_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_extra.sm_shifa_pharmacies_action')
        action['domain'] = [('institution', '=', self.id)]
        return action

    def open_pharmacist_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_extra.sm_shifa_Pharmacist_action')
        action['domain'] = [('institution', '=', self.id)]
        return action
    def _pharmacist_count(self):
        pharmacist_obj = self.env['sm.shifa.pharmacist']
        for phist in self:
            domain = [('institution', '=', phist.id)]
            pharmacist_ids = pharmacist_obj.search(domain)
            pharmacists = pharmacist_obj.browse(pharmacist_ids)
            pharmist_count = 0
            for ist_id in pharmacists:
                pharmist_count+=1
            phist.pharmacist_cuont = pharmist_count
        return True

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')
    code = fields.Char('Reference', index=True, copy=False)
    # name = fields.Char(string='Company Name')
    # branches_number = fields.Char(string='Branches Number')
    discount = fields.Float(string='Discount')
    start_date = fields.Date(string='Start Date', required=True)
    exp_date = fields.Date(string='Expiration date', required=True)
    state = fields.Selection(STATE, string='Status', readonly=True, copy=False, help="Status",
                             default=lambda *a: 'Draft')
    contract_document = fields.Binary(string='Contract Document')
    comment = fields.Text(string='Comment')
    logo = fields.Binary(string='Logo')

    qr_code = fields.Char(string='QR Code', default=lambda *a: ''.join(random.choices(string.ascii_letters, k=5)+random.choices(string.digits, k=5)))
    pharmacies_count = fields.Integer(compute=_pharmacies_count, string="Pharmacies")
    pharmacist_cuont = fields.Integer(compute=_pharmacist_count, string="Pharmacist")

    def generate_qr_code(self):
        self.qr_code = ''.join(random.choices(string.ascii_letters, k=5) + random.choices(string.digits, k=5))

    @api.model
    def create(self, vals):

        vals['code'] = self.env['ir.sequence'].next_by_code('sm.shifa.pharmacy.chain')
        existing_records = self.env['res.partner'].search([('name', '=', vals['name'])])
        if len(existing_records) > 0:
            raise ValidationError('Pharmacy chain value must be unique')
        else:
            return super(PharmacyChain, self).create(vals)

    def make_active(self):
        return self.write({'state': 'Active'})

    def make_expired(self):
        self.search([('state', '=', 'Active'), ('exp_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Expired'
        })

    def pharmacy_active_action(self):
        self.search([('state', '=', 'Draft'), ('start_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Active'
        })

    def write(self, vals):
        vals['state'] = self._compute_start_expired_date()
        return super(PharmacyChain, self).write(vals)

    def _compute_start_expired_date(self):
        pharmacy_obj = self.env['sm.shifa.pharmacy.chain']
        count_start = pharmacy_obj.search(
            [('state', '=', 'Active'), ('start_date', '<=', fields.Date.to_string(date.today()))])
        # print(count_start)
        if count_start:
            count_expired = pharmacy_obj.search(
                [('state', '=', 'Active'), ('exp_date', '<=', fields.Date.to_string(date.today()))])
            if count_expired:
                return 'Expired'
            else:
                return 'Active'
        else:
            return 'Draft'

    @api.onchange('discount')
    def _check_discount(self):
        therapist_obj = self.env['sm.shifa.instant.consultancy.charge']
        domain = [('consultancy_name', '=', 'Instant Consultation (Pharmacy)')]
        instance = therapist_obj.search(domain)
        discount = instance.charge
        half_price = 1 * int(discount) # 0.5 0.95
        if self.discount > discount or self.discount > half_price:
            raise ValidationError("Discount is not allowed")

    # @api.onchange('exp_date')
    # def _manually_activate(self):
    #     # print(self.exp_date)
    #     # print(self.state)
    #     self.search([('state', '=', 'Expired'), ('exp_date', '<=', fields.Date.to_string(date.today()))]).write({
    #         'state': 'Active'
    #     })