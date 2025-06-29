from datetime import datetime

from odoo import models, fields, api


class ShifaHomeRounding(models.Model):
    _name = 'sm.shifa.home.rounding'

    _description = 'Patient Home Rounding Management'

    STATUS = [
        ('Draft', 'Draft'),
        ('Completed', 'Completed'),
    ]

    EVOLUTION = [
        ('Status Quo', 'Status Quo'),
        ('Improving', 'Improving'),
        ('Worsening', 'Worsening'),
    ]

    def _get_patient_rounding(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )

    name = fields.Char(string='Rounding #', size=128, required=True, default=lambda *a: '/')
    admission_id = fields.Many2one('oeh.medical.icu.admission', string='Home Admission #', readonly=False,
                                   states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)],
                                           'Cancelled': [('readonly', True)]})
    register_walk_in = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment')

    date = fields.Datetime(string='Date & Time', required=True, readonly=False,
                           states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)],
                                   'Cancelled': [('readonly', True)]}, default=lambda *a: datetime.now())
    health_professional = fields.Many2one('res.users', string='Visit Responsible', required=True, readonly=False,
                                          states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)],
                                                  'Cancelled': [('readonly', True)]}, default=lambda self: self._uid)
    patient = fields.Many2one('oeh.medical.patient', related='admission_id.patient', string='Patient',
                              help="Patient Name", readonly=True, store=True)
    pain = fields.Boolean(string='Pain', help="Check if the patient is in pain", readonly=True,
                          states={'Draft': [('readonly', False)]})
    pain_level = fields.Integer(string='Pain Level', help="Enter the pain level, from 1 to 10", readonly=True,
                                states={'Draft': [('readonly', False)]})
    potty = fields.Boolean(string='Potty', help="Check if the patient needs to urinate / defecate", readonly=True,
                           states={'Draft': [('readonly', False)]})
    position = fields.Boolean(string='Position',
                              help="Check if the patient needs to be repositioned or is unconfortable", readonly=True,
                              states={'Draft': [('readonly', False)]})
    proximity = fields.Boolean(string='Proximity',
                               help="Check if personal items, water, alarm, ... are not in easy reach", readonly=True,
                               states={'Draft': [('readonly', False)]})
    pump = fields.Boolean(string='Pumps', help="Check if personal items, water, alarm, ... are not in easy reach",
                          readonly=True, states={'Draft': [('readonly', False)]})
    personal_needs = fields.Boolean(string='Personal needs', help="Check if the patient requests anything",
                                    readonly=True, states={'Draft': [('readonly', False)]})
    systolic = fields.Integer(string='Systolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    diastolic = fields.Integer(string='Diastolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    bpm = fields.Integer(string='Heart Rate', help="Heart rate expressed in beats per minute", readonly=True,
                         states={'Draft': [('readonly', False)]})
    respiratory_rate = fields.Integer(string='Respiratory Rate',
                                      help="Respiratory rate expressed in breaths per minute", readonly=True,
                                      states={'Draft': [('readonly', False)]})
    osat = fields.Integer(string='Oxygen Saturation', help="Oxygen Saturation(arterial)", readonly=True,
                          states={'Draft': [('readonly', False)]})
    temperature = fields.Float(string='Temperature', help="Temperature in celsius", readonly=True,
                               states={'Draft': [('readonly', False)]})
    diuresis = fields.Integer(string='Diuresis', help="volume in ml", readonly=True,
                              states={'Draft': [('readonly', False)]})
    urinary_catheter = fields.Integer(string='Urinary Catheter', readonly=True, states={'Draft': [('readonly', False)]})
    glycemia = fields.Integer(string='Glycemia', help="Blood Glucose level", readonly=True,
                              states={'Draft': [('readonly', False)]})
    depression = fields.Boolean(string='Depression Signs', help="Check this if the patient shows signs of depression",
                                readonly=True, states={'Draft': [('readonly', False)]})
    evolution = fields.Selection(EVOLUTION, string='Evolution', readonly=True, states={'Draft': [('readonly', False)]})
    evaluation_end_date = fields.Datetime(string='End date & time', readonly=True,
                                          states={'Draft': [('readonly', False)]})

    round_summary = fields.Text(string="Round Summary", readonly=True, states={'Draft': [('readonly', False)]})
    warning = fields.Boolean(string='Warning',
                             help="Check this box to alert the supervisor about this patient rounding. A warning icon will be shown in the rounding list",
                             readonly=True, states={'Draft': [('readonly', False)]})
    procedures = fields.One2many('oeh.medical.patient.rounding.procedure', 'name', string='Procedures',
                                 help="List of the procedures in this rounding. Please enter the first one as the main procedure",
                                 readonly=True, states={'Draft': [('readonly', False)]})
    medicaments = fields.One2many('oeh.medical.patient.rounding.medicines', 'name', string='Medicines',
                                  help="List of the medicines assigned in this rounding", readonly=True,
                                  states={'Draft': [('readonly', False)]})
    state = fields.Selection(STATUS, string='State', readonly=True, default=lambda *a: 'Draft')
    weight = fields.Integer(string='Weight', help="Measured weight, in kg", readonly=True,
                            states={'Draft': [('readonly', False)]})
    admission_id = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission #', readonly=False)#, states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)], 'Cancelled': [('readonly', True)]}


    def set_to_completed(self):
        return self.write({'state': 'Completed', 'evaluation_end_date': datetime.now()})

    def print_patient_evaluation(self):
        return self.env.ref('oehealth_extra_addons.action_report_patient_rounding_evaluation').report_action(self)


class ShifaPatientHomeRoundingProcedures(models.Model):
    _name = 'oeh.medical.patient.rounding.procedure'
    _description = 'Patient Procedures For Roundings'

    name = fields.Many2one('sm.shifa.home.rounding', string='Rouding')
    procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', required=True)
    notes = fields.Text('Notes')


class ShifaPatientHomeRoundingMedicines(models.Model):
    _name = 'oeh.medical.patient.rounding.medicines'
    _description = 'Patient Medicines For Roundings'

    name = fields.Many2one('sm.shifa.home.rounding', string='Rounding')
    medicine = fields.Many2one('oeh.medical.medicines', string='Medicines',
                               domain=[('medicament_type', '=', 'Medicine')], required=True)
    qty = fields.Integer("Quantity", default=lambda *a: 1)
    notes = fields.Text('Comment')



