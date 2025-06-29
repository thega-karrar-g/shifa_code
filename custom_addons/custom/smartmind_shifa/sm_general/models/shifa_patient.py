from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
import string
import random
import logging
_logger = logging.getLogger(__name__)


class ShifaPatient(models.Model):
    _inherit = "oeh.medical.patient"
    _rec_name = 'name'
    # id : id field name one or more
    _add_rec_name = ['ssn', 'mobile']

    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]

    PATIENT_STATE = [
        ('single_service', 'Single Service'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ]

    def action_open_record(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oeh.medical.patient',
            'res_id': self.id,
            'view_mode': 'form',
        }
    # Compute methods
    def _hvd_app_count(self):
        oe_apps = self.env['sm.shifa.hvd.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.hvd_app_count = app_count
        return True

    def _hhc_app_count(self):
        oe_apps = self.env['sm.shifa.hhc.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.hhc_app_count = app_count
        return True

    def _phy_app_count(self):
        oe_apps = self.env['sm.shifa.physiotherapy.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.phy_app_count = app_count
        return True

    def _pcr_app_count(self):
        oe_apps = self.env['sm.shifa.pcr.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.pcr_app_count = app_count
        return True

    def _default_kas_country(self):
            return self.env['res.country'].search([('code', '=', 'SA')], limit=1).id

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if not self._rec_name:
            _logger.warning("Cannot execute name_search, no _rec_name defined on %s", self._name)
        elif not (name == '' and operator == 'ilike'):
            for rec_name in self._add_rec_name:
                args += ['|', (rec_name, operator, name)]
            args += [(self._rec_name, operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    state = fields.Selection(PATIENT_STATE, string="state", readonly=True, default=lambda *a: 'single_service')
    # count appointments for current patient
    hvd_app_count = fields.Integer(compute=_hvd_app_count, string="HVD Appointments")
    hhc_app_count = fields.Integer(compute=_hhc_app_count, string="HHC Appointments")
    phy_app_count = fields.Integer(compute=_phy_app_count, string="Physiotherapy Appointments")
    pcr_app_count = fields.Integer(compute=_pcr_app_count, string="PCR Appointments")

    weight = fields.Float(string='Weight (kg)')
    nationality = fields.Char(string='Nationality')
    ksa_nationality = fields.Selection(NATIONALITY_STATE, string="Nationality", default='KSA', readonly=True)
    country_id = fields.Many2one('res.country', default=_default_kas_country)
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Company Name")

    ssn = fields.Char(size=256, string='ID Number', required=True, unique=True)
    dob = fields.Date(string='Date of Birth', required=False)
    age = fields.Char(size=32, string='Patient Age')
    sex = fields.Selection(string='Gender', required=False)
    marital_status = fields.Selection(string='Marital Status')
    blood_type = fields.Selection(string='Blood Type')
    rh = fields.Selection(string='Rh')

    nursing_assessment_ids = fields.One2many('sm.shifa.nursing.assessment', 'patient', string='Nursing Assessment')
    home_questionnaire_ids = fields.One2many('sm.shifa.safe.home.visit.screening', 'patient',
                                             string='Safe Home Visit Screening')

    family_accounts_show = fields.Boolean()
    # parent_id = fields.Many2one('')
    parent_id = fields.Many2one('oeh.medical.patient', string='Patient Custodian', default=0)
    children_lines = fields.One2many('oeh.medical.patient', 'id', default=0)
    child_name = fields.Char(related='parent_id.name')
    child_ssn = fields.Char(related='parent_id.ssn')
    child_mobile = fields.Char(related='parent_id.mobile')
    second_mobile = fields.Char(string='Second Mobile')
    house_number = fields.Char(string='House Number')

    fcm_token = fields.Char('FCM Token')  # Patient Mobile App Token
    patient_image = fields.Binary(string='Patient Image')
    external_facility = fields.Many2one('sm.shifa.external.facility.contract')

    def set_to_discharge(self):
        return self.write({'state': 'discharged'})

    def set_to_admit(self):
        return self.write({'state': 'admitted'})

    def set_to_single_service(self):
        return self.write({'state': 'single_service'})

    # email = fields.Char('Email', required=True)

    @api.model
    def create(self, vals):
        if vals.get('ssn'):
            #vals['patient_password'] = ''.join(random.choices(string.digits, k=4))
            found_id_number = self.env['oeh.medical.patient'].search_count([('ssn', '=', vals['ssn'])])
            if found_id_number > 0:
                raise ValidationError("The entered ID Number is already found in database")

        record = super(ShifaPatient, self).create(vals)
        # Call the SMS function after record creation
        record.action_send_sms()
        return record
    # def create(self, vals):
    #     pat_obj = self.env['oeh.medical.patient']
    #     # vals['patient_image'] = vals['image_1920']
    #     if vals['ssn']:
    #         vals['patient_password'] = ''.join(random.choices(string.digits, k=4))
    #         found_id_number = pat_obj.search_count([('ssn', '=', vals['ssn'])])
    #         if found_id_number > 0:
    #             raise ValidationError("The entered ID Number is already found in database")
    #         else:
    #             return super(ShifaPatient, self).create(vals)
    #     else:
    #         return super(ShifaPatient, self).create(vals)

    def _is_ssn_found(self, ssn):
        pat_obj = self.env['oeh.medical.patient']
        if ssn:
            domain = [('ssn', '=', ssn)]
            found_id_number = pat_obj.search_count(domain)
            if found_id_number > 0:
                return True
            else:
                return False

    @api.onchange('ssn')
    def validate_ssn(self):
        if self.ssn:
            match = re.match('^[1-2]\d{9}$', self.ssn)
            if not match:
                raise ValidationError('Please note, the length of ID Number must 10 numbers and must start with 1 or 2')

    @api.onchange('mobile','second_mobile')
    def mobile_check(self):
        if self.mobile:
            if self.mobile[0:4] == '9665':
                if str(len(self.mobile)) == '12':
                    pass
                else:
                    length = len(self.mobile)
                    raise ValidationError("mobile number is {} digits should be 12 digits".format(length))
            else:
                raise ValidationError(_("Invalid mobile number, should be start with '9665' "))

        if self.second_mobile:
            if self.second_mobile[0:4] == '9665':
                if str(len(self.second_mobile)) == '12':
                    pass
                else:
                    length = len(self.second_mobile)
                    raise ValidationError("mobile number is {} digits should be 12 digits".format(length))
            else:
                raise ValidationError(_("Invalid mobile number, should be start with '9665' "))
    @api.onchange('ssn')
    def _change_nationality(self):
        if self.ssn:
            if self.ssn[0] == '1':
                self.ksa_nationality = 'KSA'
            elif self.ssn[0] == '2':
                self.ksa_nationality = 'NON'
            else:
                raise ValidationError(_("Invalid ID number, should be start with '1' or '2' "))

    def action_send_sms(self):
        my_model = self._name
        if self.mobile:
            msg = "اسم المسخدم :%s   " \
                  "كلمة السر :%s   " \
                  "قم بتحميل التطبيق من    " \
                  " لاجهزة الاندرويد  https://bit.ly/3OsqdDP"\
                  " لاجهزة الايفون https://apple.co/3ofu9g9 " % (
                self.ssn, str(self.patient_password))
            self.send_sms(self.mobile, msg, my_model, self.id)

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))


class OtpPatient(models.Model):
    _inherit = "oeh.medical.patient"

    otp_secret = fields.Char(string="OTP Secret")
    otp_now = fields.Integer(string="OTP Time", help="Time or remain OTP active with comparison to OTP period")
    otp_period = fields.Integer(string="OTP Period", default=90, help="Time or remain OTP active")


class ShifaFamilyPatient(models.Model):
    _inherit = "oeh.medical.patient"

    SEX = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    CARE_GIVE = [
        ('Totally Dependent', 'Totally Dependent'),
        ('Partially Dependent', 'Partially Dependent'),
        ('Requires Help in ADL', 'Requires Help in ADL'),
    ]

    date = fields.Date()
    area = fields.Char()
    patient_live_alone = fields.Boolean(string='Live Alone')
    mother = fields.Boolean()
    father = fields.Boolean()
    son = fields.Boolean()
    sisters = fields.Boolean()
    brothers = fields.Boolean()
    daughter = fields.Boolean()
    spouse = fields.Boolean()
    driver = fields.Boolean()
    housemaid = fields.Boolean()
    other = fields.Boolean()
    # Care giver 1
    cg_1_name = fields.Char()
    cg_1_relation = fields.Char()
    cg_1_age = fields.Char()
    cg_1_gender = fields.Selection(SEX, string='Gender', index=True)
    cg_1_education = fields.Char()
    cg_1_occupation = fields.Char()
    cg_1_speak_arabic = fields.Boolean()
    cg_1_speak_english = fields.Boolean()
    cg_1_smoke = fields.Boolean()
    # Care giver 2
    cg_2_name = fields.Char()
    cg_2_relation = fields.Char()
    cg_2_age = fields.Char()
    cg_2_gender = fields.Selection(SEX, string='Gender', index=True)
    cg_2_education = fields.Char()
    cg_2_occupation = fields.Char()
    cg_2_speak_arabic = fields.Boolean()
    cg_2_speak_english = fields.Boolean()
    cg_2_smoke = fields.Boolean()
    cg_2_speak_arabic = fields.Boolean()
    cg_2_speak_english = fields.Boolean()
    cg_2_smoke = fields.Boolean()
    # Other data types
    household_no = fields.Integer('Number of Household Member')
    has_same_address = fields.Boolean(string='Same Address', default=True)
    care_give = fields.Selection(CARE_GIVE)
    is_required_asmc = fields.Boolean()
    equipment_care = fields.Boolean()
    suctioning = fields.Boolean()
    medication = fields.Boolean()
    chest_physiotherapy = fields.Boolean()
    supervision = fields.Boolean()
    feeding = fields.Boolean()
    housekeeping = fields.Boolean()
    shopping = fields.Boolean()
    transportation = fields.Boolean()
    bathing = fields.Boolean()
    grooming = fields.Boolean()
    laundry = fields.Boolean()
    patient_require_24 = fields.Boolean()
    care_give_understand_res = fields.Boolean()
    house_location = fields.Char(string="House Location")
    payment_count = fields.Integer(string="Payment", compute='_payment_count')

    def _payment_count(self):
        payment = self.env['account.payment']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            app_ids = payment.search(domain)
            apps = payment.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.payment_count = app_count
        return True

    def open_account_payment(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments')
        action['domain'] = [('partner_id.id', '=', self.partner_id.id)]
        action.update({'context': {}})
        return action
class ShifaNotifyPatient(models.Model):
    _inherit = "oeh.medical.patient"

    patient_fcm_token = fields.Char('Patient FCM Token', readonly=True)
    device_type = fields.Char('Device Type', readonly=True)


class ShifaPatientInvestigation(models.Model):
    _inherit = "oeh.medical.patient"

    lab_request_ids = fields.One2many('sm.shifa.lab.request', 'patient', string='Lab Request')
    image_request_id = fields.One2many('sm.shifa.imaging.request', 'patient', string='Imaging Request')
    image_test_ids = fields.One2many('oeh.medical.imaging', 'patient', string='Imaging Test')
    investigation_ids = fields.One2many('sm.shifa.investigation', 'patient', string='Patient')


class ShifaPatientPrescription(models.Model):
    _inherit = "oeh.medical.patient"

    prescription_id = fields.One2many('oeh.medical.prescription', 'patient', string='Prescription')


class ShifaPatientPhysicianAdmission(models.Model):
    _inherit = "oeh.medical.patient"

    phy_adm_id = fields.One2many('sm.shifa.physician.admission', 'patient', string='Physician Admission')


class ShifaPatientWoundAssessment(models.Model):
    _inherit = "oeh.medical.patient"

    wound_assessment_line = fields.One2many('sm.shifa.wound.assessment', 'patient', string='Wound Assessment')


class ShifaPatientPhysiotherapy(models.Model):
    _inherit = "oeh.medical.patient"

    physiotherapy_assessment_line = fields.One2many('sm.shifa.physiotherapy.assessment', 'patient',
                                                    string='Physiotherapy Assessment')


class ShifaPatientHistoryTab(models.Model):
    _inherit = 'oeh.medical.patient'

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # History tab
    # History of present illness
    history_present_illness_show = fields.Boolean()
    history_present_illness = fields.Text()
    # review systems details
    review_systems_show = fields.Boolean()
    constitutional = fields.Boolean(default=True)
    constitutional_content = fields.Char()
    head = fields.Boolean(default=True)
    head_content = fields.Char()
    cardiovascular = fields.Boolean(default=True)
    cardiovascular_content = fields.Char()
    pulmonary = fields.Boolean(default=True)
    pulmonary_content = fields.Char()
    gastroenterology = fields.Boolean(default=True)
    gastroenterology_content = fields.Char()
    genitourinary = fields.Boolean(default=True)
    genitourinary_content = fields.Char()
    dermatological = fields.Boolean(default=True)
    dermatological_content = fields.Char()
    musculoskeletal = fields.Boolean(default=True)
    musculoskeletal_content = fields.Char()
    neurological = fields.Boolean(default=True)
    neurological_content = fields.Char()
    psychiatric = fields.Boolean(default=True)
    psychiatric_content = fields.Char()
    endocrine = fields.Boolean(default=True)
    endocrine_content = fields.Char()
    hematology = fields.Boolean(default=True)
    hematology_content = fields.Char()

    # Past medical History
    past_medical_history_show = fields.Boolean()
    past_medical_history = fields.Many2one('oeh.medical.pathology', string='Disease')
    past_medical_history_date = fields.Date(string='Date')
    past_medical_history_1st_add = fields.Many2one('oeh.medical.pathology.category', string='Disease')
    past_medical_history_1st_add_other = fields.Boolean()
    past_medical_history_1st_add_date = fields.Date(string='Date')
    past_medical_history_2nd_add = fields.Many2one('oeh.medical.pathology.category', string='Disease')
    past_medical_history_2nd_add_date = fields.Date(string='Date')
    past_medical_history_2nd_add_other = fields.Boolean()

    # Surgical History
    surgical_history_show = fields.Boolean()
    surgical_history_procedures = fields.Many2one('oeh.medical.procedure', string='Procedures')
    surgical_history_procedures_date = fields.Date(string='Date')

    surgical_history_procedures_1st_add_other = fields.Boolean()
    surgical_history_procedures_1st_add = fields.Many2one('oeh.medical.procedure', string='Procedures')
    surgical_history_procedures_1st_add_date = fields.Date(string='Date')

    surgical_history_procedures_2nd_add_other = fields.Boolean()
    surgical_history_procedures_2nd_add = fields.Many2one('oeh.medical.procedure', string='Procedures')
    surgical_history_procedures_2nd_add_date = fields.Date(string='Date')
    # Family History
    family_history_show = fields.Boolean()
    family_history = fields.Text()
    @api.onchange('drug_allergy', 'food_allergy', 'other_allergy')
    def get_selection(self):

        if self.drug_allergy:
            self.has_drug_allergy = "yes"
        else:
            self.has_drug_allergy = "no"

        if self.food_allergy:
            self.has_food_allergy = "yes"
        else:
            self.has_food_allergy = "no"

        if self.other_allergy:
            self.has_other_allergy = "yes"
        else:
            self.has_other_allergy = "no"

    @api.onchange('has_drug_allergy', 'has_food_allergy', 'has_other_allergy')
    def get_boolean(self):
        if self.has_drug_allergy == "yes":
            self.drug_allergy = True
        else:
            self.drug_allergy = False

        if self.has_food_allergy == "yes":
            self.food_allergy = True
        else:
            self.food_allergy = False

        if self.has_other_allergy == "yes":
            self.other_allergy = True
        else:
            self.other_allergy = False

    # Allergies
    allergies_show = fields.Boolean()
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy')
    drug_allergy = fields.Boolean(default=False)
    drug_allergy_content = fields.Char()

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy')
    food_allergy = fields.Boolean(default=False)
    food_allergy_content = fields.Char()

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy')
    other_allergy = fields.Boolean(default=False)
    other_allergy_content = fields.Char()

    # Personal Habits
    personal_habits_show = fields.Boolean()
    # Physical Exercise
    exercise = fields.Boolean(string='Exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day', help="How many minutes a day the patient exercises")
    # sleep
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day")
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night")
    # Smoking
    smoking = fields.Boolean(string='Smokes')
    smoking_number = fields.Integer(string='Cigarretes a Day')
    age_start_smoking = fields.Integer(string='Age Started to Smoke')

    ex_smoker = fields.Boolean(string='Ex-smoker')
    age_start_ex_smoking = fields.Integer(string='Age Started to Smoke')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking")
    second_hand_smoker = fields.Boolean(string='Passive Smoker',
                                        help="Check it the patient is a passive / second-hand smoker")
    # drink
    alcohol = fields.Boolean(string='Drinks Alcohol')
    age_start_drinking = fields.Integer(string='Age Started to Drink ', help="Date to start drinking")

    alcohol_beer_number = fields.Integer(string='Beer / day')
    alcohol_liquor_number = fields.Integer(string='Liquor / day')
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic')
    alcohol_wine_number = fields.Integer(string='Wine / day')
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking")

    # Vaccination
    vaccination_show = fields.Boolean()
    Vaccination = fields.Many2one('sm.shifa.generic.vaccines', string='Vaccine')
    vaccination_date = fields.Date(string='Date')

    Vaccination_1st_add_other = fields.Boolean()
    Vaccination_1st_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures')
    Vaccination_1st_add_date = fields.Date(string='Date')

    Vaccination_2nd_add_other = fields.Boolean()
    Vaccination_2nd_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures')
    Vaccination_2nd_add_date = fields.Date(string='Date')

    @api.onchange('cardiovascular', 'constitutional', 'head', 'pulmonary', 'genitourinary', 'gastroenterology',
                  'dermatological', 'musculoskeletal', 'neurological', 'psychiatric', 'endocrine', 'hematology')
    def _onchange_cardiovascular(self):
        if self.cardiovascular:
            self.cardiovascular_content = ''
        if self.constitutional:
            self.constitutional_content = ''
        if self.head:
            self.head_content = ''
        if self.pulmonary:
            self.pulmonary_content = ''
        if self.genitourinary:
            self.genitourinary_content = ''
        if self.gastroenterology:
            self.gastroenterology_content = ''
        if self.dermatological:
            self.dermatological_content = ''
        if self.musculoskeletal:
            self.musculoskeletal_content = ''
        if self.neurological:
            self.neurological_content = ''
        if self.psychiatric:
            self.psychiatric_content = ''
        if self.endocrine:
            self.endocrine_content = ''
        if self.hematology:
            self.hematology_content = ''


class ShifaPatientFamily(models.Model):
    _name = 'sm.shifa.family'
    _description = "Shifa Family"

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name")
    phone = fields.Char(string='Mobile', related='patient.mobile')
    ssn = fields.Char(size=256, string='National ID', related='patient.ssn')

    patient_family_id = fields.Many2one('oeh.medical.patient', index=True, ondelete='cascade')


class ShifaPatientFamilyInherit(models.Model):
    _inherit = 'oeh.medical.patient'

    patient_family_lines = fields.One2many('sm.shifa.family', 'patient_family_id', ondelete='cascade')


class ShifaPatientExternalPrescription(models.Model):
    _inherit = "oeh.medical.patient"

    ext_pre_id = fields.One2many('sm.shifa.external.prescription', 'patient', string='External Prescription')


class ShifaPatientMedicationProfile(models.Model):
    _inherit = "oeh.medical.patient"

    med_pro_id = fields.One2many('sm.shifa.medication.profile', 'patient', string='Medication Profile')
