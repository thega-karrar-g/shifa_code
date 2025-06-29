from odoo import models, fields, api


class ShifaIcuAdmission(models.Model):
    _inherit = "oeh.medical.icu.admission"

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Hospitalized', 'Hospitalized'),
        ('Discharged', 'Discharged'),
        ('Invoiced', 'Invoiced'),
        ('Cancelled', 'Cancelled')
    ]

    ADMISSION_TYPE = [
        ('Routine', 'Routine'),
        ('Maternity', 'Maternity'),
        ('Elective', 'Elective'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
        ('Other', 'Other'),
    ]

    VENTILATION_TYPE = [
        ('Non-Invasive Positive Pressure', 'Non-Invasive Positive Pressure'),
        ('ETT - Endotracheal Tube', 'ETT - Endotracheal Tube'),
        ('Tracheostomy', 'Tracheostomy'),
    ]

    icu_room = fields.Many2one('oeh.medical.icu', domain="[('state','=','Free')]", string='ICU Room #', required=False,
                               readonly=True, states={'Draft': [('readonly', False)]})
    ventilation_type = fields.Selection(VENTILATION_TYPE, string='Ventilation Type')
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft')
    # patient details
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')

    drug_allergy_content = fields.Char(string='Drug Allergy', related='patient.drug_allergy_content')
    food_allergy_content = fields.Char(string='Drug Allergy', related='patient.food_allergy_content')
    other_allergy_content = fields.Char(string='Drug Allergy', related='patient.other_allergy_content')
    # others
    admission_type = fields.Selection(ADMISSION_TYPE, string='Admission Type', required=True, readonly=True,
                                      states={'Draft': [('readonly', False)]})
    present_illness_history = fields.Char(string='History of present illness')
    evaluation_ids = fields.One2many('oeh.medical.evaluation', 'icuAdmission', string='Evaluation IDs')
    nursing_plan = fields.Text()
    # physician_admission_ids = fields.One2many('sm.shifa.physician.admission', 'icu_admission_id')
    # nursing_assessment_ids = fields.One2many('sm.shifa.nursing.assessment', 'icu_admission_id')
    # patient_treatment_ids = fields.One2many('sm.shifa.patient.treatment', 'icu_admission_id')

    # prescribed_medicines = fields.One2many('oeh.medical.inpatient.prescribed.medicine', 'icu_admission_id',
    #                                        string='Prescribed Medicines', readonly=True,
    #                                        states={'Hospitalized': [('readonly', False)]})
    # consumed_medicines = fields.One2many('oeh.medical.inpatient.consumed.medicine', 'icu_admission_id',
    #                                      string='Consumed Medicines', readonly=True,
    #                                      states={'Hospitalized': [('readonly', False)]})


# Add medical histories to icu admission
class ShifaIcuAdmissionMedicalHistory(models.Model):
    _inherit = "oeh.medical.icu.admission"

    hbv_infection_chk = fields.Boolean(string='HBV Infection')
    hbv_infection_remarks = fields.Text(string='HBV Infection Remarks')
    dm_chk = fields.Boolean(string='DM')
    dm_remarks = fields.Text(string='DM Remarks')
    ihd_chk = fields.Boolean(string='IHD')
    ihd_remarks = fields.Text(string='IHD Remarks')
    cold_chk = fields.Boolean(string='Cold')
    cold_remarks = fields.Text(string='Cold Remarks')
    hypertension_chk = fields.Boolean(string='Hypertension')
    hypertension_remarks = fields.Text(string='Hypertension Remarks')
    surgery_chk = fields.Boolean(string='Surgery')
    surgery_remarks = fields.Text(string='Surgery Remarks')
    others_past_illness = fields.Text(string='Others Past Illness')
    nsaids_chk = fields.Boolean(string='Nsaids')
    nsaids_remarks = fields.Text(string='Nsaids Remarks')
    aspirin_chk = fields.Boolean(string='Aspirin')
    aspirin_remarks = fields.Text(string='Aspirin Remarks')
    laxative_chk = fields.Boolean(string='Laxative')
    laxative_remarks = fields.Text(string='Laxative Remarks')
    others_drugs = fields.Text(string='Others Drugs')
    lmp_chk = fields.Boolean(string='LMP')
    lmp_dt = fields.Date(string='Date')
    menorrhagia_chk = fields.Boolean(string='Menorrhagia')
    menorrhagia_remarks = fields.Text(string='Menorrhagia Remarks')
    dysmenorrhoea_chk = fields.Boolean(string='Dysmenorrhoea')
    dysmenorrhoea_remarks = fields.Text(string='Dysmenorrhoea Remarks')
    bleeding_pv_chk = fields.Boolean(string='Bleeding PV')
    bleeding_pv_remarks = fields.Text(string='Bleeding PV Remarks')
    last_pap_smear_chk = fields.Boolean(string='Last PAP smear')
    last_pap_smear_remarks = fields.Text(string='Last PAP smear Remarks')


# Inheriting icu admission module to add information to manage Patient's Lifestyles
class ShifaIcuAdmissionLifeStyle(models.Model):
    _inherit = 'oeh.medical.icu.admission'

    SEXUAL_PREFERENCE = [
        ('Heterosexual', 'Heterosexual'),
        ('Homosexual', 'Homosexual'),
        ('Bisexual', 'Bisexual'),
        ('Transexual', 'Transexual'),
    ]

    SEXUAL_PRACTICES = [
        ('Safe / Protected sex', 'Safe / Protected sex'),
        ('Risky / Unprotected sex', 'Risky / Unprotected sex'),
    ]

    SEXUAL_PARTNERS = [
        ('Monogamous', 'Monogamous'),
        ('Polygamous', 'Polygamous'),
    ]

    ANTI_CONCEPTIVE = [
        ('None', 'None'),
        ('Pill / Minipill', 'Pill / Minipill'),
        ('Male Condom', 'Male Condom'),
        ('Vasectomy', 'Vasectomy'),
        ('Female Sterilisation', 'Female Sterilisation'),
        ('Intra-uterine Device', 'Intra-uterine Device'),
        ('Withdrawal Method', 'Withdrawal Method'),
        ('Fertility Cycle Awareness', 'Fertility Cycle Awareness'),
        ('Contraceptive Injection', 'Contraceptive Injection'),
        ('Skin Patch', 'Skin Patch'),
        ('Female Condom', 'Female Condom'),
    ]

    SEXUAL_ORAL = [
        ('None', 'None'),
        ('Active', 'Active'),
        ('Passive', 'Passive'),
        ('Both', 'Both'),
    ]

    SEXUAL_ANAL = [
        ('None', 'None'),
        ('Active', 'Active'),
        ('Passive', 'Passive'),
        ('Both', 'Both'),
    ]

    exercise = fields.Boolean(string='Exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day', help="How many minutes a day the patient exercises")
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day")
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night")
    number_of_meals = fields.Integer('Meals / day')
    eats_alone = fields.Boolean(string='Eats alone', help="Check this box if the patient eats by him / herself.")
    salt = fields.Boolean(string='Salt', help="Check if patient consumes salt with the food")
    coffee = fields.Boolean(string='Coffee')
    coffee_cups = fields.Integer(string='Cups / day', help="Number of cup of coffee a day")
    soft_drinks = fields.Boolean(string='Soft Drinks (sugar)',
                                 help="Check if the patient consumes soft drinks with sugar")
    diet = fields.Boolean(string='Currently on a Diet', help="Check if the patient is currently on a diet")
    diet_info = fields.Char(string='Diet Info', size=256, help="Short description on the diet")
    smoking = fields.Boolean(string='Smokes')
    smoking_number = fields.Integer(string='Cigarretes a Day')
    ex_smoker = fields.Boolean(string='Ex-smoker')
    second_hand_smoker = fields.Boolean(string='Passive Smoker',
                                        help="Check it the patient is a passive / second-hand smoker")
    age_start_smoking = fields.Integer(string='Age Started to Smoke')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking")
    alcohol = fields.Boolean(string='Drinks Alcohol')
    age_start_drinking = fields.Integer(string='Age Started to Drink ', help="Date to start drinking")
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking")
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic')
    alcohol_beer_number = fields.Integer(string='Beer / day')
    alcohol_wine_number = fields.Integer(string='Wine / day')
    alcohol_liquor_number = fields.Integer(string='Liquor / day')
    drug_usage = fields.Boolean(string='Drug Habits')
    ex_drug_addict = fields.Boolean(string='Ex Drug Addict')
    drug_iv = fields.Boolean(string='IV Drug User', help="Check this option if the patient injects drugs")
    age_start_drugs = fields.Integer(string='Age Started Drugs ', help="Age of start drugs")
    age_quit_drugs = fields.Integer(string='Age Quit Drugs ', help="Date of quitting drugs")
    # drugs = fields.Many2many('oeh.medical.recreational.drugs', 'oeh_medical_patient_recreational_drugs_rel', 'partner_id', 'oeh_drugs_recreational_id', string='Recreational Drugs', help="Name of drugs that the patient consumes")
    traffic_laws = fields.Boolean(string='Obeys Traffic Laws', help="Check if the patient is a safe driver")
    car_revision = fields.Boolean(string='Car Revision',
                                  help="Maintain the vehicle. Do periodical checks - tires, engine, breaks ...")
    car_seat_belt = fields.Boolean(string='Seat Belt', help="Safety measures when driving : safety belt")
    car_child_safety = fields.Boolean(string='Car Child Safety',
                                      help="Safety measures when driving : child seats, proper seat belting, not seating on the front seat, ....")
    home_safety = fields.Boolean(string='Home Safety',
                                 help="Keep safety measures for kids in the kitchen, correct storage of chemicals, ...")
    motorcycle_rider = fields.Boolean(string='Motorcycle Rider', help="The patient rides motorcycles")
    helmet = fields.Boolean(string='Uses Helmet', help="The patient uses the proper motorcycle helmet")
    lifestyle_info = fields.Text(string='Extra Information')
    sexual_preferences = fields.Selection(SEXUAL_PREFERENCE, string='Sexual Orientation')
    sexual_practices = fields.Selection(SEXUAL_PRACTICES, string='Sexual Practices')
    sexual_partners = fields.Selection(SEXUAL_PARTNERS, string='Sexual Partners')
    sexual_partners_number = fields.Integer(string='Number of Sexual Partners')
    first_sexual_encounter = fields.Integer(string='Age first Sexual Encounter')
    anticonceptive = fields.Selection(ANTI_CONCEPTIVE, string='Anticonceptive Method')
    sex_oral = fields.Selection(SEXUAL_PARTNERS, string='Oral Sex')
    sex_anal = fields.Selection(SEXUAL_PARTNERS, string='Anal Sex')
    prostitute = fields.Boolean(string='Prostitute', help="Check if the patient (he or she) is a prostitute")
    sex_with_prostitutes = fields.Boolean(string='Sex with Prostitutes',
                                          help="Check if the patient (he or she) has sex with prostitutes")
    sexuality_info = fields.Text(string='Sexuality Information')


# Inheriting icu admission module to add information to manage Patient's Investigation
class ShifaIcuAdmissionInvestigation(models.Model):
    _inherit = 'oeh.medical.icu.admission'

    lab_test_ids = fields.One2many('oeh.medical.lab.test', 'icuAdmission', string='Lab Test IDs')
    image_test_ids = fields.One2many('oeh.medical.imaging', 'icuAdmission', string='Image Test')
    investigation_ids = fields.One2many('sm.shifa.investigation', 'icuAdmission', string='Home Admission')
    comments = fields.Text(string='Consultation Comment')


class ShifaImagingTestForIcuAdmission(models.Model):
    _inherit = 'oeh.medical.imaging'

    icuAdmission = fields.Many2one('oeh.medical.icu.admission', string='Home Admission')


class ShifaLabTestForIcuAdmission(models.Model):
    _inherit = 'oeh.medical.lab.test'

    icuAdmission = fields.Many2one('oeh.medical.icu.admission', string='Home Admission')


class ShifaEvaluationForIcuAdmission(models.Model):
    _inherit = 'oeh.medical.evaluation'

    icuAdmission = fields.Many2one('oeh.medical.icu.admission', string='Home Admission')


class ShifaIcuAdmissionExamination(models.Model):
    _inherit = 'oeh.medical.icu.admission'

    home_rounding_ids = fields.One2many('sm.shifa.home.rounding', 'admission_id', string='Home Rounding', readonly=True, states={'Hospitalized': [('readonly', False)], 'On Ventilation': [('readonly', False)], 'Ventilation Removed': [('readonly', False)]})

    # Anthropometry
    weight = fields.Float(string="Weight (kg)")
    height = fields.Float(string="Height (cm)")
    abdominal_circ = fields.Float(string="Abdominal Circumference")
    head_circumference = fields.Float(string="Head Circumference")
    bmi = fields.Float(string="Body Mass Index (BMI)")

    # Vital Signs
    temperature = fields.Float(string="Temperature (celsius)")
    systolic = fields.Integer(string="Systolic Pressure")
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    osat = fields.Integer(string="Oxygen Saturation")
    diastolic = fields.Integer(string="Diastolic Pressure")
    bpm = fields.Integer(string="Heart Rate")

    # Glucose
    glycemia = fields.Float(string="Glycemia")
    hba1c = fields.Float(string="Glycated Hemoglobin")

    # Nutrition
    malnutrition = fields.Boolean(string="Malnutrition")
    dehydration = fields.Boolean(string="Dehydration")

    head_neck = fields.Boolean()
    head_neck_content = fields.Char()

    cardiovascular = fields.Boolean()
    cardiovascular_content = fields.Char()

    chest = fields.Boolean()
    chest_content = fields.Char()

    abdomen = fields.Boolean()
    abdomen_content = fields.Char()

    musculo = fields.Boolean()
    musculo_content = fields.Char()

    cns = fields.Boolean()
    cns_content = fields.Char()

    psychiatric = fields.Boolean()
    psychiatric_content = fields.Char()

    rectal = fields.Boolean()
    rectal_content = fields.Char()

    skin = fields.Boolean()
    skin_content = fields.Char()

    urine_test = fields.Boolean()
    urine_test_content = fields.Char()

    develop = fields.Boolean()
    develop_content = fields.Char()

    # Photo Images
    image1 = fields.Binary(string="Image 1")
    image2 = fields.Binary(string="Image 2")


class ShifaIcuAdmissionReviewSystems(models.Model):
    _inherit = 'oeh.medical.icu.admission'

    constitutional = fields.Boolean()
    constitutional_content = fields.Char()

    head = fields.Boolean()
    head_content = fields.Char()

    cardiovascular = fields.Boolean()
    cardiovascular_content = fields.Char()

    pulmonary = fields.Boolean()
    pulmonary_content = fields.Char()

    gastroenterology = fields.Boolean()
    gastroenterology_content = fields.Char()

    genitourinary = fields.Boolean()
    genitourinary_content = fields.Char()

    dermatological = fields.Boolean()
    dermatological_content = fields.Char()

    musculoskeletal = fields.Boolean()
    musculoskeletal_content = fields.Char()

    neurological = fields.Boolean()
    neurological_content = fields.Char()

    psychiatric = fields.Boolean()
    psychiatric_content = fields.Char()

    endocrine = fields.Boolean()
    endocrine_content = fields.Char()

    hematology = fields.Boolean()
    hematology_content = fields.Char()


class ShifaPrescribedMedicamentForIcuAdmission(models.Model):
    _inherit = 'oeh.medical.inpatient.prescribed.medicine'

    icu_admission_id = fields.Many2one('oeh.medical.icu.admission', string='Home Admission', index=True)
    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient Admission Reference', required=False, index=True)


class ShifaConsumedMedicamentForIcuAdmission(models.Model):
    _inherit = 'oeh.medical.inpatient.consumed.medicine'

    icu_admission_id = fields.Many2one('oeh.medical.icu.admission', string='Home Admission', index=True)
    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient Admission Reference', required=False, index=True)



