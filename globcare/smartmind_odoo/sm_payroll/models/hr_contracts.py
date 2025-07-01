from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class ExternalContracts(models.Model):
    _inherit = 'hr.contract'

    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]
    MARITAL_STATUS = [
        ('single', 'Single'),
        ('married', 'Married')
    ]
    CONTRACT_TYPE = [
        ('part_time', 'Part Time'),
        ('full_time', 'Full Time'),
        ('freelance', 'Freelance')
    ]
    CONTRACT_DURATION = [
        ('one_year', 'One Year'),
        ('two_years', 'Two Years'),
        ('open', 'Open')
    ]
    EMPLOYEE_TYPE = [
        ('admin', 'Administrative'),
        ('medical_staff', 'Medical Staff')
    ]

    def _default_kas_country(self):
        res = self.env['res.country'].search([('code', '=', 'SA')], limit=1).id
        return res

    #  nationality
    ksa_nationality = fields.Selection(NATIONALITY_STATE, string="Nationality", default='KSA')
    country_id = fields.Many2one('res.country', default=_default_kas_country)
    # social status
    marital_status = fields.Selection(MARITAL_STATUS, string="Marital Status")
    family_members = fields.Char(string="# Family Members")
    # contract details
    contract_type = fields.Selection(CONTRACT_TYPE, string="Contract Type")
    contract_duration = fields.Selection(CONTRACT_DURATION, string="Contract Duration")
    # employee details
    employee_type = fields.Selection(EMPLOYEE_TYPE, string="Employee Type")
    scfhs_license = fields.Binary(string='SCFHS License')
    scfhs_end_date = fields.Datetime(string="Expired Date")
    bls_license = fields.Binary(string='BLS License')
    bls_end_date = fields.Datetime(string="Expired Date")
    acls_license = fields.Binary(string='ACLS License')
    acls_end_date = fields.Datetime(string="Expired Date")
    moh_license = fields.Binary(string='MOH License')
    moh_end_date = fields.Datetime(string="Expired Date")
    malpractice_insurance = fields.Binary(string='Malpractice Insurance')

    #  Monthly company's liability
    medical_insurance = fields.Monetary('Medical Insurance', tracking=True, help="Employee's medical insurance.")
    travel_tickets = fields.Monetary('Travel Tickets', tracking=True, help="Employee's Travel Tickets.")

    @api.onchange("contract_duration")
    def get_end_date(self):
        if self.contract_duration == "one_year":
            self.date_end = self.date_start + relativedelta(years=1)
        elif self.contract_duration == "two_years":
            self.date_end = self.date_start + relativedelta(years=2)
        else:
            self.date_end = False

    # smart icon for allocation from time off
    def open_allocation_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_odoo.hr_contact_allocation_action_all')
        return action

