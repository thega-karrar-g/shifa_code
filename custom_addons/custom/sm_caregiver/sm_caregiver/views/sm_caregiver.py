from odoo import models, fields, api
from datetime import datetime
import dateutil.parser
from odoo.exceptions import ValidationError


class SmCaregiver(models.Model):
    _name = 'sm.caregiver'
    _description = "Caregiver Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('start', 'Start'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Reviewed', 'Reviewed'),
    ]

    def update_visal(self):
        return self.write({'date_vital_signs': datetime.now()})

    def update_pain(self):
        return self.write({'date_pain_present': datetime.now()})

    def update_prescribed_medicine(self):
        return self.write({'date_prescribed_medicine': datetime.now()})

    @api.depends('medicine_state')
    def _compute_medicine_list(self):
        for rec in self:
            medicine_obj = self.env['sm.caregiver.medicine.schedule']
            domain = [('state', '=', rec.medicine_state), ('caregiver_id', '=', rec.id)]
            medicine = medicine_obj.search(domain)
            if medicine:
                rec.schedule_lines = medicine.ids
            else:
                rec.schedule_lines = False
    # Get Medication profile for patient
    @api.depends('patient')
    def get_medication_profile(self):
        for rec in self:
            medication_obj = False
            if rec.patient:
                medication_obj = self.env['sm.shifa.medication.profile'].search([('patient', '=', rec.patient.id), ('state_app', '=' ,'active')])
            if medication_obj:
                rec.medication_profile_line = [(6, 0, medication_obj.ids)]
            else:
                rec.medication_profile_line = False


    name = fields.Char('Reference', index=True, copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})

    caregiver = fields.Many2one('oeh.medical.physician', string='First Caregiver', readonly=True, required=True,
                                states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_second = fields.Many2one('oeh.medical.physician', string='Second Caregiver', readonly=True,
                                       states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_third = fields.Many2one('oeh.medical.physician', string='Third Caregiver', readonly=True,
                                      states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])

    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True, tracking=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')

    special_instructions_show = fields.Boolean()
    special_instructions = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    notification_id = fields.One2many('sm.physician.notification', 'care_giver_not_id',
                                      string='care notification', readonly=True,
                                      states={'start': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    nurse_name = fields.Many2one('oeh.medical.physician', string='Head Nurse', readonly=True,
                                 states={'start': [('readonly', False)]},
                                 domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)])
    phy_asse = fields.Many2one('sm.shifa.physician.assessment', string='Phy_Assessment#',
                               readonly=True, states={'Draft': [('readonly', False)]},
                               domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")

    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis')
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add')
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add2')
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add3')
    medical_care_plan = fields.Text(related='phy_asse.medical_care_plan')

    prescribed_medicine_main = fields.One2many('sm.caregiver.main.patient.medicine',
                                               'caregiver_id', readonly=True,
                                               states={'start': [('readonly', False)]},
                                               string='Patient Medications', tracking=True)

    medication_profile_line = fields.Many2many('sm.shifa.medication.profile', string='Medical Profile', compute='get_medication_profile', store=True,
                                             readonly=True, states={'start': [('readonly', False)]})
    vital_signs_lines = fields.One2many('sm.caregiver.vital.signs.lines', 'caregiver_vital_signs_id',
                                        string='Caregiver Vital Signs', readonly=True)
    pain_present_lines = fields.One2many('sm.caregiver.pain.present.lines', 'caregiver_pain_present_id',
                                         string='Pain Present line', readonly=True)
    given_medicine_lines = fields.One2many('sm.caregiver.given.medicine.lines', 'given_medicine_id',
                                                string='Given Medicine', readonly=True,
                                                states={'In Progress': [('readonly', False)]})

    objective_lines = fields.One2many('sm.caregiver.observation.lines', 'caregiver_objective_id', string='Objective',
                                      readonly=True)
    missed_medicine_lines = fields.One2many('sm.caregiver.missed.medicine.lines', 'missed_medicine_id',
                                            string='Missed Medicine', readonly=True,
                                            states={'In Progress': [('readonly', False)]})
    cancel_medicine_lines = fields.One2many('sm.caregiver.cancel.medicine.lines', 'cancel_medicine_id', string='Canceled Medicine', readonly=True,
                                            states={'In Progress': [('readonly', False)]})

    notification_id = fields.One2many('sm.physician.notification', 'caregiver_notification_id',
                                      string='Caregiver Notification', readonly=True,
                                      states={'start': [('readonly', False)]})
    M_STATE = [
        ('given', 'Given'),
        ('canceled', 'Canceled'),
        ('missed', 'Missed'),
        ('no_need', 'No need'),
    ]

    medicine_state = fields.Selection(M_STATE, string='State', tracking=True)
    schdule_line_domain = fields.Char()
    schedule_lines = fields.One2many('sm.caregiver.medicine.schedule', 'caregiver_id', ondelete='cascade',
                                     domain=[('state', '=', 'given')])
    missed_schedule_lines = fields.One2many('sm.caregiver.medicine.schedule', 'caregiver_id', ondelete='cascade',
                                     domain=[('state', '=', 'missed')])
    canceled_schedule_lines = fields.One2many('sm.caregiver.medicine.schedule', 'caregiver_id', ondelete='cascade',
                                     domain=[('state','=','canceled')])
    no_need_schedule_lines = fields.One2many('sm.caregiver.medicine.schedule', 'caregiver_id', ondelete='cascade',
                                     domain=[('state','=','no_need')])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.caregiver')
        return super(SmCaregiver, self).create(vals)

    def set_to_in_progress(self):
        return self.write({'state': 'In Progress'})

    def set_to_start(self):
        return self.write({'state': 'start', 'start_date': datetime.now()})

    def set_to_completed(self):
        return self.write({'state': 'Completed', 'completed_date': datetime.now()})

    def set_to_reviewed(self):
        for record in self:
            user_obj = self.env.user.id
            record.nurse_name = self.env['oeh.medical.physician'].search([('oeh_user_id', '=',user_obj)])
        return self.write({'state': 'Reviewed'})

    def set_to_draft(self):
        return self.write({'state': 'start'})


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    caregiver_notification_id = fields.Many2one('sm.caregiver', string='Caregiver Notification', ondelete='cascade')


class SmMedicationProfileCaregiverFollowup(models.Model):
    _inherit = 'sm.shifa.medication.profile'

    medication_id = fields.Many2one('sm.caregiver', string='caregiver', ondelete='cascade')

    @api.model
    def create(self, values):
        new_medicine = super(SmMedicationProfileCaregiverFollowup, self).create(values)

        # Log the creation in the chatter of the related caregiver record
        subtype_id = self.env['mail.message.subtype'].search([('name', '=', 'Comment')], limit=1).id
        caregiver = new_medicine.medication_id
        if caregiver:
            caregiver.message_post(
                body=f"Added new medication profile had been created",
                subtype_id=subtype_id, # Use the appropriate subtype
            )

        return new_medicine

class CaregiverVitalSignsLines(models.Model):
    _name = "sm.caregiver.vital.signs.lines"
    _description = "CareGiver Vital Signs Lines"

    systolic = fields.Integer()
    heart_rate = fields.Integer()
    diastolic = fields.Integer()
    respiratory_rate = fields.Integer()
    blood_sugar = fields.Integer(string="Blood Sugar")
    temperature = fields.Float()
    done = fields.Boolean(default=False)
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], string='O2 Sat')
    oxygen_saturation = fields.Float(string='% O2')
    date = fields.Datetime(default=lambda *a: datetime.now())
    caregiver_vital_signs_id = fields.Many2one('sm.caregiver', string='vital signs', index=True, ondelete='cascade')
    day = fields.Char(string='Day', compute='_get_day')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', readonly=True,
                                domain=[('role_type', '=', 'C'), ('active', '=', True)])

    @api.depends('date')
    def _get_day(self):
        for rec in self:
            if rec.date:
                b = dateutil.parser.parse(str(rec.date)).date()
                rec.day = str(b.strftime("%A"))
            else:
               rec.day = ""

class CaregiverPainPresentLines(models.Model):
    _name = "sm.caregiver.pain.present.lines"
    _description = "CareGiver Pain Present Lines"

    pain_score = fields.Selection([
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ])
    pain_area = fields.Char()
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ])
    date = fields.Datetime(default=lambda *a: datetime.now())
    done_pain = fields.Boolean(default=False)
    comment = fields.Char(string='Comment')
    day = fields.Char(string='Day', compute='_get_day')
    caregiver_pain_present_id = fields.Many2one('sm.caregiver', string='Doctor', index=True, ondelete='cascade')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', readonly=True,
                                domain=[('role_type', '=', 'C'), ('active', '=', True)])
    # date get day name
    @api.depends('date')
    def _get_day(self):
        for rec in self:
            if rec.date:
                b = dateutil.parser.parse(str(rec.date)).date()
                rec.day = str(b.strftime("%A"))
            else:
                rec.day = ""

class CaregiverGivenMedicineLines(models.Model):
    _name = "sm.caregiver.given.medicine.lines"
    _description = "CareGiver Given Medicine Lines"

    given_medicines = fields.Char(string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")

    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    given_medicine_text = fields.Char()
    date_given_medicine = fields.Datetime(default=lambda *a: datetime.now())
    done_given = fields.Boolean(default=False)
    day = fields.Char(string='Day', compute='_get_day')
    given_medicine_id = fields.Many2one('sm.caregiver', string='Given Medicine', index=True, ondelete='cascade')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', readonly=True,
                                domain=[('role_type', '=', 'C'), ('active', '=', True)])
    @api.depends('date_given_medicine')
    def _get_day(self):
        for rec in self:
            if rec.date_given_medicine:
                b = dateutil.parser.parse(str(rec.date_given_medicine)).date()
                rec.day = str(b.strftime("%A"))
            else:
                rec.day = ""


class CaregiverObjectiveLines(models.Model):
    _name = "sm.caregiver.observation.lines"
    _description = "Caregiver Observation Lines"

    EG_FP = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]
    DN_NA = [
        ('Done', 'Done'),
        ('Not Done', 'Not Done'),
        ('NA', 'NA'),
    ]

    nutritional_status = fields.Selection(EG_FP)
    type_diet = fields.Char(string="Type of Diet")
    feeding = fields.Selection([
        ('enteral', 'Enteral'),
        ('oral', 'Oral')
    ])
    breakfast = fields.Boolean(string="Breakfast")
    lunch = fields.Boolean(string="Lunch")
    dinner = fields.Boolean(string="Dinner")
    # sleep
    sleeping_pattern = fields.Selection(EG_FP)
    first_number_hours = fields.Char(string="Number of hours")
    second_number_hours = fields.Char(string="Number of hours")
    third_number_hours = fields.Char(string="Number of hours")
    first_from = fields.Char(string="From")
    second_from = fields.Char(string="From")
    third_from = fields.Char(string="From")
    first_to = fields.Char(string="To")
    second_to = fields.Char(string="To")
    third_to = fields.Char(string="To")
    # bathing
    bathing_shower = fields.Selection(DN_NA)
    bath_done = fields.Selection([
        ('normally', 'Normally'),
        ('on_bed', 'On bed')
    ])
    bathing_shower_text = fields.Char()
    # bed_bath = fields.Selection(DN_NA)
    # bed_bath_text = fields.Char()
    # hair_care = fields.Selection(DN_NA)
    # hair_care_text = fields.Char()
    mouth_care = fields.Selection(DN_NA)
    mouth_care_text = fields.Char()
    nail_care = fields.Selection(DN_NA)
    nail_care_text = fields.Char()
    shaving = fields.Selection(DN_NA)
    shaving_text = fields.Char()
    bowel_bladder_care = fields.Selection(DN_NA)
    bowel_number = fields.Char()
    bowel_time = fields.Char()
    bowel_bladder_care_text = fields.Char()
    bowel_urine = fields.Selection([
        ('done', 'Done'),
        ('not_done', 'Not Done'),
        ('na', 'NA'),
    ])
    bowel_urine_amount = fields.Char()
    bowel_urine_time = fields.Char()
    bowel_urine_text = fields.Char()
    diaper_changes = fields.Selection([
        ('done', 'Done'),
        ('not_done', 'Not Done'),
        ('na', 'NA'),
    ])
    diaper_number = fields.Char()
    diaper_time = fields.Char()
    diaper_text = fields.Char()
    # dressing_grooming = fields.Selection(DN_NA)
    # dressing_grooming_text = fields.Char()
    meals_feeding = fields.Selection(DN_NA)
    meals_feeding_text = fields.Char()
    # ambulation = fields.Selection(DN_NA)
    # ambulation_text = fields.Char()
    positioning_bed = fields.Selection(DN_NA)
    position = fields.Selection(
        [('ambulatory', 'Ambulatory'),
         ('bedridden', 'Bedridden')]
    )
    position_lines = fields.One2many('sm.caregiver.position.lines', 'object_id')
    # positioning_bed_text = fields.Char()
    # positioning_wheelchair = fields.Selection(DN_NA)
    # positioning_wheelchair_text = fields.Char()
    permitted_exercise = fields.Selection(DN_NA)
    permitted_exercise_text = fields.Char()
    # transfers_bed_to_chair = fields.Selection(DN_NA)
    # transfers_bed_to_chair_text = fields.Char()
    urinary_catheter_care = fields.Selection(DN_NA)
    urinary_catheter_text = fields.Char()
    nasogastric_tube = fields.Selection(DN_NA)
    nasogastric_tube_text = fields.Char()
    tracheostomy_care = fields.Selection(DN_NA)
    tracheostomy_care_text = fields.Char()
    percutaneous_endoscopic_gastrostomy = fields.Selection(DN_NA)
    percutaneous_endoscopic_text = fields.Char()
    medication = fields.Selection(DN_NA)
    medication_text = fields.Char()
    other_box = fields.Boolean()
    other_box_text = fields.Char()
    progress_noted_show = fields.Boolean()
    progress_noted = fields.Text()
    special_care = fields.Char(string='Special Care Done')
    date = fields.Datetime(default=lambda *a: datetime.now())
    caregiver_objective_id = fields.Many2one('sm.caregiver', string='objective', index=True, ondelete='cascade')
    day = fields.Char(string='Day', compute='_get_day')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', domain=[('role_type', '=', 'C'), ('active', '=', True)])
    # date get day name
    @api.depends('date')
    def _get_day(self):
        for rec in self:
            if rec.date:
                b = dateutil.parser.parse(str(rec.date)).date()
                rec.day = str(b.strftime("%A"))
            else:
                rec.day = ""


class CaregiverMissedMedicineLines(models.Model):
    _name = "sm.caregiver.missed.medicine.lines"
    _description = "Caregiver Missed Medicine Lines"

    missed_medicines = fields.Char(string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")

    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    missed_medicine_text = fields.Char()
    date_missed_medicine = fields.Datetime(default=lambda *a: datetime.now())
    done_missed = fields.Boolean(default=False)
    missed_medicine_id = fields.Many2one('sm.caregiver', string='Missed Medicine', index=True,
                                         ondelete='cascade')
    day = fields.Char(string='Day', compute='_get_day')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', readonly=True,
                                domain=[('role_type', '=', 'C'), ('active', '=', True)])
    @api.depends('date_missed_medicine')
    def _get_day(self):
        for rec in self:
            if rec.date_missed_medicine:
                b = dateutil.parser.parse(str(rec.date_missed_medicine)).date()
                rec.day = str(b.strftime("%A"))
            else:
                rec.day = ""

class CaregiverCanceledMedicineLines(models.Model):
    _name = "sm.caregiver.cancel.medicine.lines"
    _description = "Caregiver Canceled Medicine Lines"

    canceled_medicines = fields.Char(string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")

    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    canceled_medicine_text = fields.Char()
    date_cancel_medicine = fields.Datetime(default=lambda *a: datetime.now())
    done_canceled = fields.Boolean(default=False)
    cancel_medicine_id = fields.Many2one('sm.caregiver', string='Canceled Medicine', index=True,
                                         ondelete='cascade')
    day = fields.Char(string='Day', compute='_get_day')
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver', readonly=True,
                                domain=[('role_type', '=', 'C'), ('active', '=', True)])
    @api.depends('date_cancel_medicine')
    def _get_day(self):
        for rec in self:
            if rec.date_cancel_medicine:
                b = dateutil.parser.parse(str(rec.date_cancel_medicine)).date()
                rec.day = str(b.strftime("%A"))
            else:
               rec.day = ""

class CaregiverPositionLines(models.Model):
    _name = "sm.caregiver.position.lines"
    _description = "Caregiver Positions Lines"

    positions = fields.Selection([
        ('right', 'Right'),
        ('left', 'Left'),
        ('prone', 'Prone'),
        ('supine', 'Supine'),
    ], string='Positions')
    from_time = fields.Char('From')
    to_time = fields.Char('To')
    object_id = fields.Many2one('sm.caregiver.observation.lines', ondelete='cascade')
    caregiver_position_id = fields.Many2one('sm.caregiver', string='caregiver', index=True, store=True
                                   , related='object_id.caregiver_objective_id', ondelete='cascade')