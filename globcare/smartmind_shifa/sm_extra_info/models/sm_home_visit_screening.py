from odoo import api, fields, models
import datetime


class ShifaSafeHomeVisitScreening(models.Model):
    _name = "sm.shifa.safe.home.visit.screening"
    _description = "Home questionnaire for Patient"
    _rec_name = 'home_visit_screening_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]

    def set_to_start(self):
        return self.write({'state': 'Start'})

        #     admitted date method

    def _get_anticoagulation(self):
        """Return default anticoagulation value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def set_to_admitted(self):
        admission_date = False
        for ina in self:
            if ina.admission_date:
                admission_date = ina.admission_date
            else:
                admission_date = datetime.datetime.now()
        return self.write({'state': 'Admitted', 'admission_date': admission_date})

        #     discharge date time method

    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    home_visit_screening_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly='1')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    nurse_name = fields.Many2one('oeh.medical.physician', string='Visit Responsible', readonly=True, required=True,
                                 states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'HHCN'), ('active', '=', True)],
                                 default=_get_anticoagulation)
    QUES_YES_NO_NA = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]

    # ------------------ the first tab page ------------------#
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    admission_date = fields.Datetime(string='Admission Date', readonly='1')
    discharge_date = fields.Datetime(string='Discharge Date', readonly='1')
    clinician_checklist_show = fields.Boolean()
    cl_objection_home_visit = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                               readonly=True, states={'Start': [('readonly', False)]})

    cl_venue_home_visit = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                           readonly=True, states={'Start': [('readonly', False)]})
    # cl_venue_home_visit_comments
    venue_home_visit_comments = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    cl_medical_record_indicate = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes', oldname='cl_4',
                                                  readonly=True, states={'Start': [('readonly', False)]})
    cl_medical_record_indicate_check = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    cl_medical_record_indicate_comments = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    cl_provide_hands_assistance_patient = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                           readonly=True, states={'Start': [('readonly', False)]})
    cl_health_status_occupants_visitors = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                           readonly=True, states={'Start': [('readonly', False)]})
    cl_health_status_occupants_visitors_expl = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    cl_evening_visits_appropriate = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                     readonly=True, states={'Start': [('readonly', False)]})

    # ------------------ the second tab page ------------------#

    patient_and_household_occupants_show = fields.Boolean()
    pa_patient_history_psychiatric_violent = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                              readonly=True, states={'Start': [('readonly', False)]})
    pa_patient_history_alcohol = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                  readonly=True, states={'Start': [('readonly', False)]})
    pa_occupants_frequent_visitors = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                      readonly=True, states={'Start': [('readonly', False)]})
    pa_occupants_frequent_visitors_list_other = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    pa_will_present_visits = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                              readonly=True, states={'Start': [('readonly', False)]})
    pa_history_psychiatric_behaviour_significant_drug = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                                         readonly=True,
                                                                         states={'Start': [('readonly', False)]})
    pa_female_family_member_caregiver = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                         readonly=True, states={'Start': [('readonly', False)]})
    pa_household_occupants_smoke = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                    readonly=True, states={'Start': [('readonly', False)]})

    # ------------------ the third tab page ------------------#

    animals_Pest_show = fields.Boolean()
    an_animals_inside_house = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                               readonly=True, states={'Start': [('readonly', False)]})
    an_animal_placed_elsewhere_whilst_HC = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                            readonly=True, states={'Start': [('readonly', False)]})
    an_pest_rodents_infestation = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                   readonly=True, states={'Start': [('readonly', False)]})
    an_animals_pest_explanation = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # ------------------ the fourth tab page ------------------#

    access_to_property_show = fields.Boolean()
    ac_road_conditions_dangerous = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                    readonly=True, states={'Start': [('readonly', False)]})
    ac_difficult_find_house = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                               readonly=True, states={'Start': [('readonly', False)]})
    ac_difficulty_accessing_property = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                        readonly=True, states={'Start': [('readonly', False)]})
    ac_path_front_door_even = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                               readonly=True, states={'Start': [('readonly', False)]})
    ac_steps_front_door = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                           readonly=True, states={'Start': [('readonly', False)]})
    ac_steps_front_door_list = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    ac_entrance_well_lit = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                            readonly=True, states={'Start': [('readonly', False)]})
    ac_adequate_street_lighting = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                   readonly=True, states={'Start': [('readonly', False)]})
    ac_lighting_within_house_adequate = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                         readonly=True, states={'Start': [('readonly', False)]})
    ac_floors_stable_clear_obstacles = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                        readonly=True, states={'Start': [('readonly', False)]})
    ac_ventilation_within_house_adequate = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                            readonly=True, states={'Start': [('readonly', False)]})
    ac_ventilation_within_house_adequate_suggest_modification = fields.Text(readonly=True,
                                                                            states={'Start': [('readonly', False)]})
    ac_air_conditioning_heater_adequate_house = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                                 readonly=True, states={'Start': [('readonly', False)]})
    ac_air_conditioning_heater_adequate_house_suggest_modification = fields.Text(readonly=True, states={
        'Start': [('readonly', False)]})
    ac_entrance_wide_enough_wheelchair_access = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                                 readonly=True, states={'Start': [('readonly', False)]})
    ac_entrance_wide_enough_wheelchair_access_suggest_modification = fields.Text(readonly=True, states={
        'Start': [('readonly', False)]})
    ac_kitchen_appliances_adequate = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                      readonly=True, states={'Start': [('readonly', False)]})
    ac_kitchen_appliances_adequate_suggest_modification = fields.Text(readonly=True,
                                                                      states={'Start': [('readonly', False)]})
    ac_laundry_facilities_available = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                       readonly=True, states={'Start': [('readonly', False)]})
    ac_laundry_facilities_available_suggest_modification = fields.Text(readonly=True,
                                                                       states={'Start': [('readonly', False)]})
    ac_toilet_accessible_wheelchair = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                       readonly=True, states={'Start': [('readonly', False)]})
    ac_toilet_accessible_wheelchair_suggest_modification = fields.Text(readonly=True,
                                                                       states={'Start': [('readonly', False)]})
    ac_safety_rails_available = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                 readonly=True, states={'Start': [('readonly', False)]})
    ac_safety_rails_available_suggest_modification = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    ac_access_property_explanation_comments = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # ------------------ the fifth tab page ------------------#
    fire_gas_electrical_hazard_show = fields.Boolean()
    fire_extinguisher_available = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                   readonly=True, states={'Start': [('readonly', False)]})
    fire_extinguisher_available_suggest_modification = fields.Text(readonly=True,
                                                                   states={'Start': [('readonly', False)]})

    smoke_fire_detector_available = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                     readonly=True, states={'Start': [('readonly', False)]})
    smoke_fire_detector_available_suggest_modification = fields.Text(readonly=True,
                                                                     states={'Start': [('readonly', False)]})

    grounded_electrical_wall_socket_available = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                                 readonly=True, states={'Start': [('readonly', False)]})
    grounded_electrical_wall_socket_available_suggest_modification = fields.Text(readonly=True, states={
        'Start': [('readonly', False)]})

    difficulties_getting_mobile_phone_reception = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    difficulties_getting_mobile_phone_reception_details = fields.Text(readonly=True,
                                                                      states={'Start': [('readonly', False)]})

    internet_access_house = fields.Selection(QUES_YES_NO_NA, required=True, default='Yes',
                                             readonly=True, states={'Start': [('readonly', False)]})
    internet_access_house_details = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    register_walk_in = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment')

    referral_id = fields.One2many('sm.shifa.referral', 'home_questionnaire_ref_id', string='Internal Referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['home_visit_screening_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.safe.home.visit.screening')
        return super(ShifaSafeHomeVisitScreening, self).create(vals)

# class ShifaReferralInherit(models.Model):
#     _inherit = 'sm.shifa.referral'
#
#     home_questionnaire_ref_id = fields.Many2one('sm.shifa.safe.home.visit.screening', string='home questionnaire', ondelete='cascade')
