from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class Vaccines(models.Model):
    _name = 'sm.shifa.vaccines'
    _description = 'Vaccines'
    _rec_name = 'vaccines_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]
    YES_NO = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    VACCINATION = [
        ('Influenza (0.25 ml)', 'Influenza (0.25 ml)'),
        ('Tdap (0.5 ml)', 'Tdap (0.5 ml)'),
        ('MMR (0.5 ml)', 'MMR (0.5 ml)'),
        ('Varicella (0.5 ml)', 'Varicella (0.5 ml)'),
        ('Herpes Zoster (0.5 ml)', 'Herpes Zoster (0.5 ml)'),
        ('HPV (0.5 ml)', 'HPV (0.5 ml)'),
        ('PPSV23 (0.5 ml)', 'PPSV23 (0.5 ml)'),
        ('PCV (0.5 ml)', 'PCV (0.5 ml)'),
        ('Hep B (0.5 ml)', 'Hep B (0.5 ml)'),
        ('MCV4 (0.5 ml)', 'MCV4 (0.5 ml)'),
        ('RV (1 ml)', 'RV (1 ml)'),
        ('D TaP (0.5 ml)', 'D TaP (0.5 ml)'),
        ('Hib (0.5 ml)', 'Hib (0.5 ml)'),
        ('IPV (0.5 ml)', 'IPV (0.5 ml)'),
        ('BCG (0.5 ml)', 'BCG (0.5 ml)'),
        ('OPV (2 gtts)', 'OPV (2 gtts)'),
        ('Measels (0.5 ml)', 'Measels (0.5 ml)'),
        ('HepA (0.5 ml)', 'HepA (0.5 ml)'),
    ]

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    def _get_vaccines(self):
        """Return default vaccines value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    vaccines_code = fields.Char('Reference', index=True, copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse', readonly=True, required=True,
                                 states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', ['HHCN', 'HN'])],
                                 default=_get_vaccines)
    # date = fields.Date(string='Date', readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')
    # conscious state
    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    # pain present
    pain_present_show = fields.Boolean()
    pain_present = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_score = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ], readonly=True, default="0", states={'Start': [('readonly', False)]})
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    # functional activity
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    #  vital signs
    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    hr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=True, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    #  check prior to administration of vaccine
    check_prior_show = fields.Boolean()
    drug_allergy_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drug_allergy_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drug_allergy_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    allergic_previous_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_previous_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_previous_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    allergic_hypersensitivty_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_hypersensitivty_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_hypersensitivty_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    any_recent_illness_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    any_recent_illness_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    any_recent_illness_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    previous_vaccination_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_temp = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

    # vaccination schedule
    vaccination_schedule_show = fields.Boolean()
    vaccination_schedule = fields.Selection([
        ('At Birth', 'At Birth'),
        ('2 Months', '2 Months'),
        ('4 Months', '4 Months'),
        ('6 Months', '6 Months'),
        ('9 Months', '9 Months'),
        ('12 Months', '12 Months'),
        ('18 Months', '18 Months'),
        ('24 Months', '24 Months'),
        ('4-6 Years old', '4-6 Years old'),
        ('11 Years', '11 Years'),
        ('12 Years', '12 Years'),
        ('18 Years', '18 Years'),
        ('Other', 'Other'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    ADMINISTERED_OVER = [
        ('Right', 'Right'),
        ('Left', 'Left'),
    ]
    at_birth_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    at_birth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    at_birth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    at_birth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    add_other_at_birth = fields.Boolean(string='Other', readonly=True,
                                        states={'Start': [('readonly', False)]})
    add_other_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                       states={'Start': [('readonly', False)]})
    add_other_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    add_other_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                       states={'Start': [('readonly', False)]})

    add_other_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other2_at_birth = fields.Boolean(string='Other', readonly=True,
                                         states={'Start': [('readonly', False)]})
    add_other2_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                        states={'Start': [('readonly', False)]})
    add_other2_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    add_other2_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    add_other2_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                        states={'Start': [('readonly', False)]})

    add_other2_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    t_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    t_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    t_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    t_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    t_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    t_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_t_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_t_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    f_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    f_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    f_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    f_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    f_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    f_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    f_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    f_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})
    f_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_f_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_f_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    s_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    s_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    s_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    s_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    s_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})

    s_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    s_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_s_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_s_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    n_mon_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    n_mon_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    n_mon_measels_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    n_mon_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    n_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    n_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    n_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    n_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_n_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_n_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    ot_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_ot_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_ot_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oe_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oe_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oe_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oe_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oe_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oe_mon_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oe_mon_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    oe_mon_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    oe_mon_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    oe_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oe_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oe_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oe_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    tf_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})

    tf_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    tf_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    tf_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    add_other_tf_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_tf_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    fs_yea_dtap = fields.Boolean(string='D Tap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    fs_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    fs_yea_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    fs_yea_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    fs_yea_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True,
                                      states={'Start': [('readonly', False)]})
    fs_yea_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    fs_yea_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    fs_yea_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    fs_yea_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    fs_yea_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_fs_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_fs_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oo_yea_dtap = fields.Boolean(string='Tdap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oo_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oo_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oo_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    # oo_yea_dtap_administered_right = fields.Boolean(string='Right', readonly=True,
    #                                                 states={'Start': [('readonly', False)]})
    # oo_yea_dtap_administered_left = fields.Boolean(string='Left', readonly=True,
    #                                                states={'Start': [('readonly', False)]})

    oo_yea_vpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oo_yea_vpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oo_yea_vpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oo_yea_vpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oo_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oo_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    ot_yea_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_yea_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_yea_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_yea_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_ot_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_ot_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oe_yea_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_yea_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_yea_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_yea_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oe_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oe_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_influenza = fields.Boolean(string='Influenza (0.25 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_influenza_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    oth_influenza_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    oth_influenza_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    oth_tdap = fields.Boolean(string='Tdap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_tdap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_tdap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_tdap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    oth_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    oth_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    oth_herpes = fields.Boolean(string='Herpes Zoster (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_herpes_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oth_herpes_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oth_herpes_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oth_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_ppsv = fields.Boolean(string='PPSV23 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_ppsv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_ppsv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_ppsv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_hepb = fields.Boolean(string='Hep B (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_other = fields.Boolean(string='Other', readonly=True,
                               states={'Start': [('readonly', False)]})
    oth_vaccinations = fields.Char(string='Vaccination', readonly=True, states={'Start': [('readonly', False)]})
    oth_vaccinations_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    oth_vaccinations_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    oth_vaccinations_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    oth_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                    states={'Start': [('readonly', False)]})
    oth_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                           states={'Start': [('readonly', False)]})

    oth_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    oth_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oth_measels_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oth_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oth_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})

    oth_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    mother_caregiver_show = fields.Boolean()
    mother_soreness_redness_swelling = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_muscular_pain = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_headaches = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_fever = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_nausea = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})

    mother_difficulty_breathing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_coughing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_hoarse_vice_wheezing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_hives = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_paleness = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_losing_consciousness = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})

    # Nurse Notes
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    add_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['vaccines_code'] = self.env['ir.sequence'].next_by_code('vaccines.code')
        return super(Vaccines, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})

    @api.onchange('drug_allergy_yes', 'allergic_previous_yes', 'allergic_hypersensitivty_yes', 'any_recent_illness_yes',
                  'previous_vaccination_yes')
    def _check_Yes(self):
        if self.drug_allergy_yes:
            self.drug_allergy_no = False
        if self.allergic_previous_yes:
            self.allergic_previous_no = False
        if self.allergic_hypersensitivty_yes:
            self.allergic_hypersensitivty_no = False
        if self.any_recent_illness_yes:
            self.any_recent_illness_no = False
        if self.previous_vaccination_yes:
            self.previous_vaccination_no = False

    @api.onchange('drug_allergy_no', 'allergic_previous_no', 'allergic_hypersensitivty_no', 'any_recent_illness_no',
                  'previous_vaccination_no')
    def _check_No(self):
        if self.drug_allergy_no:
            self.drug_allergy_yes = False
        if self.allergic_previous_no:
            self.allergic_previous_yes = False
        if self.allergic_hypersensitivty_no:
            self.allergic_hypersensitivty_yes = False
        if self.any_recent_illness_no:
            self.any_recent_illness_yes = False
        if self.previous_vaccination_no:
            self.previous_vaccination_yes = False

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'previous_vaccination_temp',
                  'char_other_oxygen')
    def _check_vital_signs(self):
        if self.systolic_bp > 1000:
            raise ValidationError("invalid systolic BP(mmHg)")
        if self.hr_min > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature_c > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.previous_vaccination_temp > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.diastolic_br > 1000:
            raise ValidationError("invalid Diastolic BR(mmHg)")
        if self.rr_min > 100:
            raise ValidationError("invalid RR(/min)")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")
