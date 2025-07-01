from odoo import models, fields, api
import datetime
import dateutil.parser
from odoo.exceptions import ValidationError


class CareGiverFollowUp(models.Model):
    _name = 'sm.shifa.care.giver.follow.up'
    _description = 'Care Giver Follow Up'
    _rec_name = 'care_giver_follow_up_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        # ('Caregiver', 'Caregiver'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Reviewed', 'Reviewed'),
    ]

    def _get_giver(self):
        """Return default giver value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def update_visal(self):
        self.done = False
        return self.write({'date_vital_signs': datetime.datetime.now()})

    def update_pain(self):
        self.done_pain = False
        return self.write({'date_pain_present': datetime.datetime.now()})

    def update_prescribed_medicine(self):
        self.done_prescribed_medicine = False
        return self.write({'date_prescribed_medicine': datetime.datetime.now()})

    care_giver_follow_up_code = fields.Char('Reference', index=True, copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm#',
                              readonly=True, states={'Draft': [('readonly', False)]},
                              domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")

    nurse_name = fields.Many2one('oeh.medical.physician', string='Head Nurse', readonly=True,
                                 states={'Completed': [('readonly', False)]},
                                 domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)],
                                 default=_get_giver)

    caregiver = fields.Many2one('oeh.medical.physician', string='First Caregiver', readonly=True, required=True,
                                states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_second = fields.Many2one('oeh.medical.physician', string='Second Caregiver', readonly=True,
                                       states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_third = fields.Many2one('oeh.medical.physician', string='Third Caregiver', readonly=True,
                                      states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])

    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')

    special_instructions_show = fields.Boolean()
    special_instructions = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    care_giver_id = fields.Many2one('sm.shifa.care.giver', string='Care Giver', ondelete='cascade')
    notification_id = fields.One2many('sm.physician.notification', 'care_giver_not_id',
                                      string='care notification', readonly=True,
                                      states={'In Progress': [('readonly', False)]})
    # provisional_diagnosis = fields.Many2one('oeh.medical.pathology', related='phy_adm.provisional_diagnosis')
    # provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', related='phy_adm.provisional_diagnosis_add')
    # provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', related='phy_adm.provisional_diagnosis_add2')
    # provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', related='phy_adm.provisional_diagnosis_add3')
    # medical_care_plan = fields.Text(related='phy_adm.medical_care_plan')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    prescription_line = fields.One2many('sm.shifa.prescription.line', 'prescription_line_id',
                                        readonly=True)

    medication_profile_line = fields.One2many('sm.shifa.medication.profile', 'medication_line_id',
                                              related="patient.med_pro_id", readonly=True)

    @api.model
    def create(self, vals):
        vals['care_giver_follow_up_code'] = self.env['ir.sequence'].next_by_code('care.giver.follow.up')
        return super(CareGiverFollowUp, self).create(vals)

    # def set_to_caregiver(self):
    #     return self.write({'state': 'Caregiver', 'start_date': datetime.datetime.now()})

    def set_to_in_progress(self):
        return self.write({'state': 'In Progress', 'start_date': datetime.datetime.now()})

    def set_to_completed(self):
        return self.write({'state': 'Completed', 'completed_date': datetime.datetime.now()})

    def set_to_reviewed(self):
        return self.write({'state': 'Reviewed'})

    def set_to_draft(self):
        return self.write({'state': 'Draft'})

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'o2_sat')
    def _check_vital_signs(self):
        if self.systolic_bp > 1000:
            raise ValidationError("invalid systolic BP(mmHg)")
        if self.hr_min > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature_c > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.diastolic_br > 1000:
            raise ValidationError("invalid Diastolic BR(mmHg)")
        if self.rr_min > 100:
            raise ValidationError("invalid RR(/min)")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")


class ShifaVitalSignsInheritlines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.vital.signs"
    _description = "Shifa Care Giver Vital Signs Lines"

    systolic_bp = fields.Integer()
    # systolic_bp = fields.Integer(readonly=readonly_button, states={'In Progress': [('readonly', _button)]})
    hr_min = fields.Integer()
    diastolic_br = fields.Integer()
    rr_min = fields.Integer()
    temperature_c = fields.Float()
    # o2_sat = fields.Float(readonly=True, states={'In Progress': [('readonly', False)]})
    done = fields.Boolean(default=False)
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], string='O2 Sat')
    char_other_oxygen = fields.Float(string='% O2')
    date_vital_signs = fields.Datetime()
    # add_other_visal = fields.Boolean(readonly=True, states={'In Progress': [('readonly', False)]})
    vital_signs_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Doctor', index=True, ondelete='cascade')
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('date_vital_signs')
    def onchange_date(self):
        if self.date_vital_signs:
            date = str(self.date_vital_signs)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'o2_sat',
                  'char_other_oxygen')
    def _check_vital_signs(self):
        if self.systolic_bp > 1000:
            raise ValidationError("invalid systolic BP(mmHg)")
        if self.hr_min > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature_c > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.diastolic_br > 1000:
            raise ValidationError("invalid Diastolic BR(mmHg)")
        if self.rr_min > 100:
            raise ValidationError("invalid RR(/min)")
        if self.systolic_bp != 0 and self.hr_min != 0 and self.rr_min != 0 and self.diastolic_br != 0 and self.temperature_c != 0:
            if self.o2_sat:
                if self.char_other_oxygen:
                    self.done = True
                    self.date_vital_signs = datetime.datetime.now()
                    print(self.done)


class ShifaVitalSignsInherit(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    vital_signs_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.vital.signs', 'vital_signs_id',
                                        string='Walkin Schedule', readonly=True,
                                        states={'In Progress': [('readonly', False)]})


class ShifaPainPresentInheritlines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.pain.present"
    _description = "Shifa Care Giver Pain Present Lines"

    pain_score = fields.Selection([
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ])
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ])
    date_pain_present = fields.Datetime()
    done_pain = fields.Boolean(default=False)
    comment = fields.Char(string='Comment')
    day = fields.Char(string='Day')
    pain_present_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Doctor', index=True, ondelete='cascade')

    # date get day name
    @api.onchange('date_pain_present')
    def onchange_date(self):
        if self.date_pain_present:
            date = str(self.date_pain_present)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))

    @api.onchange('pain_score', 'comment')
    def _check_vital_signs(self):
        if self.pain_score and self.comment:
            self.done_pain = True
            self.date_pain_present = datetime.datetime.now()


class ShifaPainPresenInherit(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    pain_present_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.pain.present', 'pain_present_id',
                                         string='Walkin Schedule', readonly=True,
                                         states={'In Progress': [('readonly', False)]})


class ShifaPrescribedMedicineInheritlines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.prescribed.medicine"
    _description = "Shifa Care Giver Prescribed Medicine Lines"

    # @api.onchange('prescribed_medicine_id', 'phy_adm')
    # def _get_medicine(self):
    #     followup_id = 0
    #     str_id = str(self.prescribed_medicine_id.id)
    #     ids_l = str_id.split("_", 1)
    #     del ids_l[0]
    #     for i in ids_l:
    #         followup_id = int(i)
    #     if self.phy_adm.id:
    #         self._cr.execute(
    #             "select prescribed_medicine from sm_shifa_care_giver_follow_up_main_prescribed_medicine WHERE phy_adm = {0} AND main_prescribed_medicine_id ={1}".format(
    #                 self.phy_adm.id, followup_id))
    #         record = self._cr.fetchall()
    #         brand_ids = [item for t in record for item in t]
    #         return {'domain': {'prescribed_brand_medicine': [('id', 'in', brand_ids)]}}
    #
    # @api.onchange('prescribed_brand_medicine')
    # def _get_medicine_details(self):
    #     followup_id = 0
    #     str_id = str(self.prescribed_medicine_id.id)
    #     ids_l = str_id.split("_", 1)
    #     del ids_l[0]
    #     for i in ids_l:
    #         followup_id = int(i)
    #     if self.phy_adm.id:
    #         therapist_obj = self.env['sm.shifa.care.giver.follow.up.main.prescribed.medicine']
    #         domain = [('phy_adm', '=', self.phy_adm.id), ('main_prescribed_medicine_id', '=', followup_id)]
    #         user_ids = therapist_obj.search(domain)
    #         print(user_ids)
    #         for i in user_ids:
    #             if self.prescribed_brand_medicine == i.prescribed_medicine:
    #                 print(i.prescribed_medicine)
    #                 self.dose = i.prescribed_dose
    #                 self.dose_unit = i.prescribed_dose_unit
    #                 self.common_dosage = i.prescribed_frequency

    prescribed_medicine = fields.Many2one('sm.shifa.generic.medicines', string='Medicine', help="Prescribed Medicines")
    prescribed_brand_medicine = fields.Many2one('sm.shifa.brand.medicines', string='Medicine',
                                                help="Prescribed Medicines")
    patient_medicines = fields.Many2one('sm.shifa.patient.medicines', string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")
    # end_treatment = fields.Datetime('End of treatment')
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    prescribed_medicine_text = fields.Char()
    # done_prescribed_medicine = fields.Boolean(default=True)
    date_prescribed_medicine = fields.Datetime()
    done_prescribed = fields.Boolean(default=False)
    prescribed_medicine_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Followup', index=True,
                                             ondelete='cascade')
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm#')
    # prescribed_medicines = fields.Many2one(string="Prescribed Medicines")
    prescribed_medicines = fields.Char(string="Prescribed Medicines")
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('date_prescribed_medicine')
    def onchange_date(self):
        if self.date_prescribed_medicine:
            date = str(self.date_prescribed_medicine)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))

    @api.onchange('patient_medicines', 'dose', 'dose_unit', 'prescribed_medicine_text',
                  'date_prescribed_medicine')
    def _check_vital_signs(self):
        for res in self:
            if res.patient_medicines and res.dose_unit and res.common_dosage:
                if res.dose != 0 and res.prescribed_medicine_text != 0:
                    res.done_prescribed = True
                    res.date_prescribed_medicine = datetime.datetime.now()


class ShifaMissedMedicineInheritlines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.missed.medicine"
    _description = "Shifa Care Giver Prescribed Medicine Lines"

    patient_medicines = fields.Many2one('sm.shifa.patient.medicines', string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")

    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    prescribed_medicine_text = fields.Char()
    date_prescribed_medicine = fields.Datetime()
    done_prescribed = fields.Boolean(default=False)
    missed_medicine_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Followup', index=True,
                                         ondelete='cascade')
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm#')
    prescribed_medicines = fields.Char(string="Prescribed Medicines")
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('date_prescribed_medicine')
    def onchange_date(self):
        if self.date_prescribed_medicine:
            date = str(self.date_prescribed_medicine)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))

    @api.onchange('patient_medicines', 'dose', 'dose_unit', 'prescribed_medicine_text',
                  'date_prescribed_medicine')
    def _check_vital_signs(self):
        for res in self:
            if res.patient_medicines and res.dose_unit and res.common_dosage:
                if res.dose != 0 and res.prescribed_medicine_text != 0:
                    res.done_prescribed = True
                    res.date_prescribed_medicine = datetime.datetime.now()


class ShifaCanceledMedicineInheritlines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.cancel.medicine"
    _description = "Shifa Care Giver Canceled Prescribed Medicine Lines"

    patient_medicines = fields.Many2one('sm.shifa.patient.medicines', string="Medicine")
    dose = fields.Float(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")

    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    prescribed_medicine_text = fields.Char()
    date_cancel_medicine = fields.Datetime()
    done_prescribed = fields.Boolean(default=False)
    cancel_medicine_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Followup', index=True,
                                         ondelete='cascade')
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm#')
    prescribed_medicines = fields.Char(string="Prescribed Medicines")
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('date_cancel_medicine')
    def onchange_date(self):
        if self.date_cancel_medicine:
            date = str(self.date_prescribed_medicine)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))

    @api.onchange('patient_medicines', 'dose', 'dose_unit', 'prescribed_medicine_text',
                  'date_cancel_medicine')
    def _check_vital_signs(self):
        for res in self:
            if res.patient_medicines and res.dose_unit and res.common_dosage:
                if res.dose != 0 and res.prescribed_medicine_text != 0:
                    res.done_prescribed = True
                    res.date_cancel_medicine = datetime.datetime.now()


class ShifaMainPrescribedMedicine(models.Model):
    _name = "sm.shifa.care.giver.follow.up.main.prescribed.medicine"
    _description = "Shifa Caregiver Main Prescribed Medicine"

    FREQUENCY_UNIT = [
        ('Seconds', 'Seconds'),
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('When Required', 'When Required'),
    ]
    MEDICINE_STATE = [
        ('Prescribed', 'Prescribed'),
        ('External', 'External'),
    ]
    NUMBER_TIMES = [
        ('as_need', 'As Needed'),
        ('after_bf', 'After Breakfast'),
        ('after_launch', 'After Launch'),
        ('after_dinner', 'After Dinner'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ]
    select_medicine = fields.Selection(MEDICINE_STATE)
    prescribed_medicine = fields.Many2one('sm.shifa.brand.medicines')
    patient_medicines = fields.Many2one('sm.shifa.patient.medicines', string="Medicine")
    medicine_image = fields.Binary(related="patient_medicines.medicine_image")
    prescribed_frequency = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                           help="Common / standard dosage frequency for this medicines")
    prescribed_dose = fields.Float(string='Dose',
                                   help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    prescribed_dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                           help="Unit of measure for the medication to be taken")
    prescribed_dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route',
                                            help="HL7 or other standard drug administration route code.")
    prescribed_dose_form = fields.Many2one('oeh.medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    prescribed_duration = fields.Integer(string='Duration')
    main_prescribed_medicine_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Followup', index=True,
                                                  ondelete='cascade')
    prescribed_frequency_unit = fields.Selection(FREQUENCY_UNIT, 'Unit', index=True)
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm#')
    prescribed_qty = fields.Integer(string='Quantity')
    start_date = fields.Date(string="Start Date")
    stop_date = fields.Date(string="Stop Date")
    times_day = fields.Selection(NUMBER_TIMES, 'Number of times a day', index=True)
    time1 = fields.Float()
    time2 = fields.Float()
    time3 = fields.Float()
    time4 = fields.Float()
    time5 = fields.Float()
    time6 = fields.Float()


class ShifaCaregiverObjectivelines(models.Model):
    _name = "sm.shifa.care.giver.follow.up.lines.observation"
    _description = "Shifa Caregiver Observation Lines"

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

    nutritional_status_show = fields.Boolean()
    nutritional_status = fields.Selection(EG_FP)

    sleeping_pattern_show = fields.Boolean()
    sleeping_pattern = fields.Selection(EG_FP)

    task_activities_provided_show = fields.Boolean()
    bathing_shower_toilet = fields.Selection(DN_NA)
    bathing_shower_toilet_text = fields.Char()
    bed_bath = fields.Selection(DN_NA)
    bed_bath_text = fields.Char()
    hair_care = fields.Selection(DN_NA)
    hair_care_text = fields.Char()
    mouth_care = fields.Selection(DN_NA)
    mouth_care_text = fields.Char()
    nail_care = fields.Selection(DN_NA)
    nail_care_text = fields.Char()
    shaving_needs_consent = fields.Selection(DN_NA)
    shaving_needs_consent_text = fields.Char()
    bowel_bladder_care = fields.Selection(DN_NA)
    bowel_bladder_care_text = fields.Char()
    dressing_grooming = fields.Selection(DN_NA)
    dressing_grooming_text = fields.Char()
    meals_feeding = fields.Selection(DN_NA)
    meals_feeding_text = fields.Char()
    ambulation = fields.Selection(DN_NA)
    ambulation_text = fields.Char()
    positioning_bed = fields.Selection(DN_NA)
    positioning_bed_text = fields.Char()
    positioning_wheelchair = fields.Selection(DN_NA)
    positioning_wheelchair_text = fields.Char()
    permitted_exercise = fields.Selection(DN_NA)
    permitted_exercise_text = fields.Char()
    transfers_bed_to_chair = fields.Selection(DN_NA)
    transfers_bed_to_chair_text = fields.Char()
    medication = fields.Selection(DN_NA)
    medication_text = fields.Char()
    other_box = fields.Boolean()
    other_box_text = fields.Char()

    progress_noted_show = fields.Boolean()
    progress_noted = fields.Text()
    date = fields.Datetime(default=lambda *a: datetime.datetime.now())
    objective_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='objective', index=True, ondelete='cascade')
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('nutritional_status_show', 'sleeping_pattern_show')
    def onchange_date(self):
        if self.date:
            date = str(self.date)
            b = dateutil.parser.parse(date).date()
            self.day = str(b.strftime("%A"))


class ShifaPrescribedMedicineInherit(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    prescribed_medicine_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.prescribed.medicine',
                                                'prescribed_medicine_id',
                                                string='Walkin Schedule', readonly=True,
                                                states={'In Progress': [('readonly', False)]})
    missed_medicine_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.missed.medicine',
                                            'missed_medicine_id',
                                            string='Walkin Schedule', readonly=True,
                                            states={'In Progress': [('readonly', False)]})
    cancel_medicine_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.cancel.medicine',
                                            'cancel_medicine_id',
                                            string='Walkin Schedule', readonly=True,
                                            states={'In Progress': [('readonly', False)]})


class ShifaMainPrescribedMedicineInherit(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    prescribed_medicine_main = fields.One2many('sm.shifa.care.giver.follow.up.main.prescribed.medicine',
                                               'main_prescribed_medicine_id', readonly=True,
                                               states={'Draft': [('readonly', False)]},
                                               string='Prescribed Medicines')


class ShifaObjectiveInherit(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    objective_lines = fields.One2many('sm.shifa.care.giver.follow.up.lines.observation',
                                      'objective_id',
                                      string='Objective', readonly=True, states={'In Progress': [('readonly', False)]})


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    care_giver_not_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='care giver follow up',
                                        ondelete='cascade')


class ShifaPrescriptionLineCaregiverFollowup(models.Model):
    _inherit = 'sm.shifa.prescription.line'

    prescription_line_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='caregiver follow up',
                                           ondelete='cascade')


class ShifaMedicationProfileCaregiverFollowup(models.Model):
    _inherit = 'sm.shifa.medication.profile'

    medication_line_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='caregiver follow up',
                                         ondelete='cascade')
