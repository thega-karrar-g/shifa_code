from odoo import models, fields, api
from datetime import date


class ShifaExternalFacility(models.Model):
    _name = 'sm.shifa.external.facility.contract'
    _description = 'External Facility Contract'
    _inherits = {
        'res.partner': 'partner_id',
    }
    STATE = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
    ]
    state = fields.Selection(STATE, string='Status', readonly=True, copy=False, help="Status",
                             default=lambda *a: 'Draft')

    # name = fields.Char(string='Facility Name')
    contract_number = fields.Char(string='Contract Number')

    start_date = fields.Date(string="Start Date", required=True)
    exp_date = fields.Date(string="Expiration Date", required=True)
    contract_document = fields.Binary(string="Contract Document")
    image = fields.Binary(string="Image")
    comment = fields.Text(string="Comment")

    def make_active(self):
        return self.write({'state': 'Active'})

    def external_facility_active(self):
        print(self.state)
        self.search([('state', '=', 'Draft'), ('start_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Active'
        })

    def external_facility_expired(self):
        print(1)
        self.search([('state', '=', 'Active'), ('exp_date', '<=', fields.Date.to_string(date.today()))]).write({
            'state': 'Expired'
        })


