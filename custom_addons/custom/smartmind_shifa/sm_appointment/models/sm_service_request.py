from odoo import models, fields, api
from datetime import timedelta, datetime


class ShifaServiceRequest(models.Model):
    _name = 'sm.shifa.service.request'
    _description = 'Service Request'

    SERVICE_STATE = [
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('canceled', 'Canceled'),
    ]
    NATIONALITY_STATE = [
        ('yes', 'Saudi'),
        ('no', 'Non-Saudi')
    ]
    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    RH = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    # Caregiver Nationality
    CAREGIVER_NATIONALITY = [
        ('African', 'African'),
        ('Philippine', 'Philippine'),
        ('Indonesia', 'Indonesia'),
        ('Other', 'Other'),
    ]

    # calculate bmi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for r in self:
            if not r.height:
                return 0
            else:
                r.bmi = r.weight / (r.height * r.height) * 10000
                return r.bmi

    state = fields.Selection(SERVICE_STATE, string='State', readonly=False, default=lambda *a: 'received')
    name = fields.Char('Reference', index=True, copy=False)
    # patient details
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'received': [('readonly', False)]})
    # patient = fields.Char(string="Patient", required=True)
    ksa_nationality = fields.Selection(NATIONALITY_STATE, string="Nationality", default='yes')
    date = fields.Datetime(string="Service Date")
    request_date = fields.Datetime(string="Request Date")
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=False,
                      states={'received': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=False,
                           states={'received': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'processed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'processed': [('readonly', True)], 'canceled': [('readonly', True)]},
                         related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'processed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.age')
    nationality = fields.Selection(string='Nationality', readonly=False,
                              states={'processed': [('readonly', True)], 'canceled': [('readonly', True)]},
                              related='patient.ksa_nationality')
    # country_id = fields.Many2one('res.country', related='patient.ksa_nationality')

    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'processed': [('readonly', True)], 'canceled': [('readonly', True)]},
                                  related='patient.weight')

    # service details - , required=True
    service = fields.Many2one('sm.shifa.service', string='Service Name', readonly=False,
                              states={'received': [('readonly', False)]},
                              domain=[('service_type', 'in', ['Car', 'PHY', 'HHC', 'HVD'])],
                              )
    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=False,
                                    store=False)
    location = fields.Char(string='Mobile location', readonly=False, states={'received': [('readonly', False)]})
    attached_file = fields.Binary(string='Attached File 1',
                                  readonly=False, states={'received': [('readonly', False)]})
    attached_file_2 = fields.Binary(string='Attached File 2',
                                    readonly=False, states={'received': [('readonly', False)]})
    attached_file_3 = fields.Binary(string='Attached File 3',
                                    readonly=False, states={'received': [('readonly', False)]})
    # service provider
    bmi_greater_28 = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    neck_circ_greater_m43_or_f40 = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})

    # questionnaire details
    weight = fields.Float(string='Weight (kg)', readonly=False, states={'received': [('readonly', False)]})
    # neck_circ = fields.Float(string='Neck Circumference (cm)', readonly=False,
    #                          states={'received': [('readonly', False)]})
    bmi = fields.Float(compute=_compute_bmi, string='BMI', store=True)
    height = fields.Float(string='Height (cm)', readonly=False, states={'received': [('readonly', False)]})

    snore = fields.Selection(YES_NO, string="Do you snore?")
    wakeup_feeling_hasnt_sleep = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    stop_breathing_night = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    gasp_air_choke = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    is_male = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    age_50_older = fields.Selection(YES_NO, readonly=False, states={'received': [('readonly', False)]})
    comment = fields.Text(string="Comment", readonly=False, states={'received': [('readonly', False)]})
    cg_date = fields.Datetime(string='Date', default=datetime.now())
    appointment = fields.Char(string="Appointment", readonly=True)
    caregiver_nationality = fields.Selection(CAREGIVER_NATIONALITY, string='Caregiver Nationality', readonly=True, states={'received': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.service.request')
        return super(ShifaServiceRequest, self).create(vals)

    def set_to_processed(self):
        return self.write({'state': 'processed'})

    def set_to_canceled(self):
        return self.write({'state': 'canceled'})

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'Service Request')])
        sequences.write({'number_next_actual': 1})
