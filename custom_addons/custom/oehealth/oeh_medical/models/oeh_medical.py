##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

import datetime
from datetime import timedelta
import logging
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.osv import expression
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)


# Family Management
class OeHealthFamily(models.Model):
    _name = 'oeh.medical.patient.family'
    _description = 'Record Patient family information'

    FAMILY_RELATION = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Wife', 'Wife'),
        ('Husband', 'Husband'),
        ('Grand Father', 'Grand Father'),
        ('Grand Mother', 'Grand Mother'),
        ('Aunt', 'Aunt'),
        ('Uncle', 'Uncle'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Cousin', 'Cousin'),
        ('Relative', 'Relative'),
        ('Other', 'Other'),
    ]

    name = fields.Char(size=256, string='Name', required=True, help='Family Member Name')
    relation = fields.Selection(FAMILY_RELATION, string='Relation', help="Family Relation", index=True)
    age = fields.Integer(string='Age', help='Family Member Age')
    deceased = fields.Boolean(string='Deceased?', help="Mark if the family member has died")
    patient_id = fields.Many2one('oeh.medical.patient', 'Patient', required=True, ondelete='cascade', index=True)


# Patient Management
class OeHealthPatient(models.Model):
    _name = 'oeh.medical.patient'
    _description = 'Patient'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    MARITAL_STATUS = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
        ('Separated', 'Separated'),
    ]

    SEX = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    BLOOD_TYPE = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ]

    RH = [
        ('+', '+'),
        ('-', '-'),
    ]

    def _app_count(self):
        oe_apps = self.env['oeh.medical.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.app_count = app_count
        return True

    def _prescription_count(self):
        oe_pres = self.env['oeh.medical.prescription']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            pres_ids = oe_pres.search(domain)
            pres = oe_pres.browse(pres_ids)
            pres_count = 0
            for pr in pres:
                pres_count += 1
            pa.prescription_count = pres_count
        return True

    def _admission_count(self):
        oe_admission = self.env['oeh.medical.inpatient']
        for adm in self:
            domain = [('patient', '=', adm.id)]
            admission_ids = oe_admission.search(domain)
            admissions = oe_admission.browse(admission_ids)
            admission_count = 0
            for ad in admissions:
                admission_count += 1
            adm.admission_count = admission_count
        return True

    def _vaccine_count(self):
        oe_vac = self.env['oeh.medical.vaccines']
        for va in self:
            domain = [('patient', '=', va.id)]
            vec_ids = oe_vac.search(domain)
            vecs = oe_vac.browse(vec_ids)
            vecs_count = 0
            for vac in vecs:
                vecs_count += 1
            va.vaccine_count = vecs_count
        return True

    def _invoice_count(self):
        oe_invoice = self.env['account.move']
        for inv in self:
            invoice_ids = self.env['account.move'].search([('patient', '=', inv.id)])
            invoices = oe_invoice.browse(invoice_ids)
            invoice_count = 0
            for inv_id in invoices:
                invoice_count += 1
            inv.invoice_count = invoice_count
        return True

    def _patient_age(self):
        def compute_age_from_dates(patient_dob, patient_deceased, patient_dod):
            now = datetime.datetime.now()
            if (patient_dob):
                dob = datetime.datetime.strptime(patient_dob.strftime('%Y-%m-%d'), '%Y-%m-%d')
                if patient_deceased:
                    dod = datetime.datetime.strptime(patient_dod.strftime('%Y-%m-%d'), '%Y-%m-%d')
                    delta = dod - dob
                    deceased = " (deceased)"
                    years_months_days = str(delta.days // 365) + " years " + str(delta.days % 365) + " days" + deceased
                else:
                    delta = now - dob
                    years_months_days = str(delta.days // 365) + " years " + str(delta.days % 365) + " days"
            else:
                years_months_days = "No DoB !"

            return years_months_days

        for patient_data in self:
            patient_data.age = compute_age_from_dates(patient_data.dob, patient_data.deceased, patient_data.dod)
        return True

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')
    family = fields.One2many('oeh.medical.patient.family', 'patient_id', string='Family')
    ssn = fields.Char(size=256, string='National Identification Number')
    current_insurance = fields.Many2one('oeh.medical.insurance', string="Insurance",
                                        domain="[('patient','=', active_id),('state','=','Active')]",
                                        help="Insurance information. You may choose from the different insurances belonging to the patient")
    doctor = fields.Many2one('oeh.medical.physician', string='Family Doctor',
                             help="Current primary care physician / family doctor",
                             domain=[('is_pharmacist', '=', False)])
    dob = fields.Date(string='Date of Birth')
    age = fields.Char(compute=_patient_age, size=32, string='Patient Age',
                      help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field")
    sex = fields.Selection(SEX, string='Gender', index=True)
    marital_status = fields.Selection(MARITAL_STATUS, string='Marital Status')
    blood_type = fields.Selection(BLOOD_TYPE, string='Blood Type')
    rh = fields.Selection(RH, string='Rh')
    identification_code = fields.Char(string='Patient ID', size=256,
                                      help='Patient Identifier provided by the Health Center', readonly=True)
    ethnic_group = fields.Many2one('oeh.medical.ethnicity', 'Ethnic group')
    critical_info = fields.Text(string='Important disease, allergy or procedures information',
                                help="Write any important information on the patient's disease, surgeries, allergies, ...")
    general_info = fields.Text(string='General Information', help="General information about the patient")
    genetic_risks = fields.Many2many('oeh.medical.genetics', 'oeh_genetic_risks_rel', 'patient_id', 'genetic_risk_id',
                                     string='Genetic Risks')
    deceased = fields.Boolean(string='Patient Deceased ?', help="Mark if the patient has died")
    dod = fields.Date(string='Date of Death')
    cod = fields.Many2one('oeh.medical.pathology', string='Cause of Death')
    app_count = fields.Integer(compute=_app_count, string="Appointments")
    prescription_count = fields.Integer(compute=_prescription_count, string="Prescriptions")
    admission_count = fields.Integer(compute=_admission_count, string="Admission / Discharge")
    vaccine_count = fields.Integer(compute=_vaccine_count, string="Vaccines")
    invoice_count = fields.Integer(compute=_invoice_count, string="Total Invoices")
    oeh_patient_user_id = fields.Many2one('res.users', string='Responsible Odoo User')
    emergency_name = fields.Char(string='Person Name')
    emergency_phone = fields.Char(string='Emergency Phone')
    emer_contact_relation = fields.Char(string='Relation')
    emergency_address = fields.Char(string='Address')
    prescription_line = fields.One2many('oeh.medical.prescription.line', 'patient', string='Medicines', readonly=True)
    followups = fields.One2many('oeh.medical.followup', 'patient', string="Followups")
    treatments = fields.One2many('oeh.medical.treatment', 'patient', string="Treatments")
    patient_username = fields.Char('Username')
    patient_password = fields.Char('password')

    _sql_constraints = [
        ('code_oeh_patient_userid_uniq', 'unique (oeh_patient_user_id)',
         "Selected 'Responsible' user is already assigned to another patient !"),
        ('code_oeh_patient_username_uniq', 'unique (patient_username)', "Patient already exist, check your username !")
    ]

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient')
        vals['identification_code'] = sequence
        vals['is_patient'] = True
        health_patient = super(OeHealthPatient, self).create(vals)
        if health_patient:
            if not health_patient.image_1920:
                health_patient.image_1920 = "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"
        
        user = self.env['res.users'].sudo().search([
            ('partner_id','=',health_patient.partner_id.id)
        ],limit=1)
        if not user:
            portal = self.env.ref('base.group_portal').id
            user = self.env['res.users'].sudo().create({
            'partner_id': health_patient.partner_id.id,
            'name': health_patient.name,
            'login': health_patient.ssn,
            'password': health_patient.patient_password,
            'groups_id': [(6, 0, [portal])],
            })
        return health_patient

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    def print_patient_label(self):
        return self.env.ref('oehealth.action_report_patient_label').report_action(self)

    def name_get(self):
        return [(patient.id, patient.name) for patient in self]

        # return [(patient.id, '[%s] %s' % (patient.identification_code, patient.name)) for patient in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('identification_code', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def write(self, vals):
        if 'ssn' in vals:
            user = self.env['res.users'].sudo().search([('partner_id','=',self.partner_id.id)],limit=1)
            if user:
                other_user = self.env['res.users'].sudo().search([('login','=',vals['ssn']),('id','!=',user.id)])
                if not other_user:
                    user.sudo().write({"login": vals['ssn']})

        if 'patient_password' in vals:
            user = self.env['res.users'].sudo().search([('partner_id','=',self.partner_id.id)],limit=1)
            if user:
                other_user = self.env['res.users'].sudo().search([('login','=',self.ssn),('id','!=',user.id)])
                if not other_user:
                    user.sudo().write({"password": vals['patient_password']})
        
        return super().write(vals)


# Doctor Management
class OeHealthPhysicianSpeciality(models.Model):
    _name = "oeh.medical.speciality"
    _description = "Doctor Speciality"

    name = fields.Char(string='Description', size=128, help="ie, Addiction Psychiatry", required=True)
    code = fields.Char(string='Code', size=128, help="ie, ADP")

    _order = 'name'
    _sql_constraints = [
        ('code_uniq', 'unique (company_id,name)', 'The Medical Speciality code must be unique')]


class OeHealthPhysicianDegree(models.Model):
    _name = "oeh.medical.degrees"
    _description = "Doctors Degrees"

    name = fields.Char(string='Degree', size=128, required=True)
    full_name = fields.Char(string='Full Name', size=128)
    physician_ids = fields.Many2many('oeh.medical.physician', string='Doctors')

    _sql_constraints = [
        ('full_name_uniq', 'unique (company_id,name)', 'The Medical Degree must be unique')]


class OeHealthPhysician(models.Model):
    _name = "oeh.medical.physician"
    _description = "Doctor"
    _inherit = ['mail.thread']
    _inherits = {
        'hr.employee': 'employee_id',
    }

    CONSULTATION_TYPE = [
        ('Residential', 'Residential'),
        ('Visiting', 'Visiting'),
        ('Other', 'Other'),
    ]

    APPOINTMENT_TYPE = [
        ('Not on Weekly Schedule', 'Not on Weekly Schedule'),
        ('On Weekly Schedule', 'On Weekly Schedule'),
    ]

    def _app_count(self):
        oe_apps = self.env['oeh.medical.appointment']
        for pa in self:
            domain = [('doctor', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.app_count = app_count
        return True

    def _prescription_count(self):
        oe_pres = self.env['oeh.medical.prescription']
        for pa in self:
            domain = [('doctor', '=', pa.id)]
            pa.prescription_count = oe_pres.search_count(domain)

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one('hr.employee', string='Related Employee', required=True, ondelete='cascade',
                                  help='Employee-related data of the physician')
    institution = fields.Many2one('oeh.medical.health.center', string='Institution',
                                  help="Institution where doctor works")
    code = fields.Char(string='Licence ID', size=128, help="Doctor's License ID")
    speciality = fields.Many2one('oeh.medical.speciality', string='Speciality', help="Speciality Code")
    consultancy_type = fields.Selection(CONSULTATION_TYPE, string='Consultancy Type',
                                        help="Type of Doctor's Consultancy", default=lambda *a: 'Residential')
    consultancy_price = fields.Integer(string='Consultancy Charge', help="Doctor's Consultancy price")
    available_lines = fields.One2many('oeh.medical.physician.line', 'physician_id', string='Doctor Availability')
    degree_id = fields.Many2many('oeh.medical.degrees', string='Degrees')
    app_count = fields.Integer(compute=_app_count, string="Appointments")
    prescription_count = fields.Integer(compute=_prescription_count, string="Prescriptions")
    is_pharmacist = fields.Boolean(string='Pharmacist?', default=lambda *a: False)
    oeh_user_id = fields.Many2one('res.users', string='Responsible Odoo User')
    appointment_type = fields.Selection(APPOINTMENT_TYPE, string='Allow Appointment on?',
                                        default=lambda self: self.env.company.appointment_type)

    _sql_constraints = [
        ('code_oeh_physician_userid_uniq', 'unique(oeh_user_id)',
         "Selected 'Responsible' user is already assigned to another physician !")
    ]

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.onchange('address_id')
    def _onchange_address(self):
        self.work_phone = self.address_id.phone
        self.mobile_phone = self.address_id.mobile

    @api.onchange('company_id')
    def _onchange_company(self):
        address = self.company_id.partner_id.address_get(['default'])
        self.address_id = address['default'] if address else False

    @api.onchange('user_id')
    def _onchange_user(self):
        self.work_email = self.user_id.email
        self.name = self.user_id.name
        self.image = self.user_id.image

    def write(self, vals):
        # if 'name' in vals:
        #     vals['name_related'] = vals['name']
        return super(OeHealthPhysician, self).write(vals)


class OeHealthPhysicianLine(models.Model):
    # Array containing different days name
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    _name = "oeh.medical.physician.line"
    _description = "Information about doctor availability"

    name = fields.Selection(PHY_DAY, string='Available Day(s)', required=True)
    start_time = fields.Float(string='Start Time (24h format)')
    end_time = fields.Float(string='End Time (24h format)')
    physician_id = fields.Many2one('oeh.medical.physician', string='Doctor', index=True, ondelete='cascade')


# Appointment Management
class OeHealthAppointment(models.Model):
    _name = 'oeh.medical.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread']
    _order = "appointment_date desc"

    PATIENT_STATUS = [
        ('Ambulatory', 'Ambulatory'),
        ('Outpatient', 'Outpatient'),
        ('Inpatient', 'Inpatient'),
    ]

    APPOINTMENT_STATUS = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Invoiced', 'Invoiced'),
    ]

    URGENCY_LEVEL = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Medical Emergency', 'Medical Emergency'),
    ]

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    # Calculating Appointment End date
    def _get_appointment_end(self):
        for apm in self:
            end_date = False
            duration = 1
            if apm.duration:
                duration = apm.duration
            if apm.appointment_date:
                end_date = datetime.datetime.strptime(apm.appointment_date.strftime("%Y-%m-%d %H:%M:%S"),
                                                      "%Y-%m-%d %H:%M:%S") + timedelta(hours=duration)
            apm.appointment_end = end_date
        return True

    def _default_institution(self):
        company = self.env['res.company']._company_default_get('res.partner')
        return self.env['oeh.medical.health.center'].search([('company_id', '=', company.id)], limit=1)

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Appointment #', size=64, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Scheduled': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             domain=[('is_pharmacist', '=', False)], required=True, readonly=True,
                             states={'Scheduled': [('readonly', False)]}, default=_get_physician)
    appointment_date = fields.Datetime(string='Appointment Date', required=True, readonly=True,
                                       states={'Scheduled': [('readonly', False)]}, default=datetime.datetime.now())
    appointment_end = fields.Datetime(compute=_get_appointment_end, string='Appointment End Date', readonly=True,
                                      states={'Scheduled': [('readonly', False)]})
    duration = fields.Float(string='Duration (HH:MM)', readonly=True, states={'Scheduled': [('readonly', False)]},
                            default=lambda self: self.env.company.appointment_duration)
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center",
                                  readonly=True, states={'Scheduled': [('readonly', False)]})
    urgency_level = fields.Selection(URGENCY_LEVEL, string='Urgency Level', readonly=True,
                                     states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Normal')
    comments = fields.Text(string='Comments', readonly=True, states={'Scheduled': [('readonly', False)]})
    patient_status = fields.Selection(PATIENT_STATUS, string='Patient Status', readonly=True,
                                      states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Inpatient')
    state = fields.Selection(APPOINTMENT_STATUS, string='State', readonly=True, default=lambda *a: 'Scheduled')

    prescription_line = fields.One2many('oeh.medical.prescription', 'appointment', string='Prescription Lines',
                                        readonly=False, states={'Invoiced': [('readonly', True)]})
    treatment_line = fields.One2many('oeh.medical.treatment', 'appointment', string='Treatment Lines',
                                     readonly=False, states={'Invoiced': [('readonly', True)]})
    labtest_line = fields.One2many('oeh.medical.lab.test', 'appointment', string='Lab Test Lines',
                                   readonly=False, states={'Invoiced': [('readonly', True)]})
    evaluation_ids = fields.One2many('oeh.medical.evaluation', 'appointment', string='Evaluation')
    #  evaluation_ids = fields.One2many('oeh.medical.evaluation', 'appointment', string='Evaluation',
    #                                      readonly=False, states={'Invoiced': [('readonly', True)]})
    move_id = fields.Many2one('account.move', string='Invoice #', copy=False)

    @api.model
    def create(self, vals):
        if vals.get('doctor') and vals.get('appointment_date'):
            self.check_physician_availability(vals.get('doctor'), vals.get('appointment_date'))

        # Generate next appointment sequence
        company = self.env['res.company']._company_default_get('oeh.medical.appointment')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.appointment'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            if vals.get('doctor') and vals.get('appointment_date'):
                self.check_physician_availability(vals.get('doctor'), vals.get('appointment_date'))
            values = {
                'name': 'Appointments (' + str(company.name) + ')',
                'code': 'oeh.medical.appointment',
                'company_id': company.id,
                'prefix': 'AP',
                'padding': 4,
            }
            self.env['ir.sequence'].sudo().create(values)
            health_appointment = models.Model.create(self, vals)
            return health_appointment
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.appointment')
            health_appointment = super(OeHealthAppointment, self).create(vals)
            return health_appointment

    def write(self, values):
        health_appointment = super(OeHealthAppointment, self).write(values)
        return health_appointment

    def check_physician_availability(self, doctor, appointment_date):
        available = False
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        patient_line_obj = self.env['oeh.medical.physician.line']
        need_to_check_availability = False

        query_doctor_availability = _("select appointment_type from oeh_medical_physician where id=%s") % (doctor)
        self.env.cr.execute(query_doctor_availability)
        val = self.env.cr.fetchone()
        if val and val[0]:
            if val[0] == "On Weekly Schedule":
                need_to_check_availability = True

        # check if doctor is working on selected day of the week
        if need_to_check_availability:
            selected_day = datetime.datetime.strptime(appointment_date, DATETIME_FORMAT).strftime('%A')

            if selected_day:
                avail_days = patient_line_obj.search([('name', '=', str(selected_day)), ('physician_id', '=', doctor)],
                                                     limit=1)

                if not avail_days:
                    raise UserError(_('Doctor is not available on selected day!'))
                else:
                    # get selected day's start and end time

                    phy_start_time = self.get_time_string(avail_days.start_time).split(':')
                    phy_end_time = self.get_time_string(avail_days.end_time).split(':')

                    user_pool = self.env['res.users']
                    user = user_pool.browse(self.env.uid)
                    tz = pytz.timezone(user.partner_id.tz) or pytz.utc

                    # get localized dates
                    appointment_date = pytz.utc.localize(
                        datetime.datetime.strptime(appointment_date, DATETIME_FORMAT)).astimezone(tz)

                    t1 = datetime.time(int(phy_start_time[0]), int(phy_start_time[1]), 0)
                    t3 = datetime.time(int(phy_end_time[0]), int(phy_end_time[1]), 0)

                    # get appointment hour and minute
                    t2 = datetime.time(appointment_date.hour, appointment_date.minute, 0)

                    if not (t2 >= t1 and t2 <= t3): # if not (t2 > t1 and t2 < t3):
                        raise UserError(_('Doctor is not available on selected time!'))
                    else:
                        available = True
        return available

    def get_time_string(self, duration):
        result = ''
        currentHours = int(duration // 1)
        currentMinutes = int(round(duration % 1 * 60))
        if (currentHours <= 9):
            currentHours = "0" + str(currentHours)
        if (currentMinutes <= 9):
            currentMinutes = "0" + str(currentMinutes)
        result = str(currentHours) + ":" + str(currentMinutes)
        return result

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def set_to_invoiced(self):
        invoice_control = self.env.company.appointment_invoice_control
        if invoice_control == 'normal':
            invoice_lines = self.get_consultation_invoice_lines()
            default_journal = self._get_default_journal()

            # Create Invoice
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient.partner_id.id,
                'patient': self.patient.id,
                'invoice_date': datetime.datetime.now().date(),
                'date': datetime.datetime.now().date(),
                'ref': "Appointment # : " + self.name,
                'appointment': self.id,
                'invoice_line_ids': invoice_lines
            })
            if self.env.company.stock_deduction_method == 'invoice_create':
                invoice.oeh_process_inventories()
            self.write({'state': 'Invoiced', 'move_id': invoice.id})
        else:
            view_id = self.env.ref('oehealth.view_oeh_medical_appointment_wizard').id
            return {'type': 'ir.actions.act_window',
                    'name': _('Create Invoice'),
                    'res_model': 'oeh.medical.appointment.invoice.wizard',
                    'target': 'new',
                    'view_mode': 'form',
                    'views': [[view_id, 'form']],
                    }

    def get_consultation_invoice_lines(self):
        invoice_lines = []
        for acc in self:
            price = acc.doctor.consultancy_price

            # Prepare Invoice lines
            # invoice_lines.append((0, 0, {
            #         'name': 'Consultancy',
            #         'display_type': 'line_section',
            #         'account_id': False,
            #         'sequence': 1,
            #     }))
            invoice_lines.append((0, 0, {
                'display_type': False,
                'quantity': 1.0,
                'name': 'Consultancy Charge for ' + acc.name,
                'price_unit': price,
                'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                    'uom.product_uom_unit').id or False,
                'sequence': 2,
            }))
        return invoice_lines

    def get_appointment_items_invoice_lines(self, with_consultancy=False):
        invoice_lines = []
        for acc in self:
            sequence = 0

            if with_consultancy:
                consultancy_invoice_lines = acc.get_consultation_invoice_lines()
                invoice_lines.extend(consultancy_invoice_lines)
                sequence = 2

            # Create Invoice lines for Treatment
            if acc.treatment_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Treatment',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))
                for treat_line in acc.treatment_line:
                    if treat_line.treatment_items:
                        for item in treat_line.treatment_items:
                            sequence += 1
                            invoice_lines.append((0, 0, {
                                'display_type': False,
                                'quantity': item.qty,
                                'name': item.name.name,
                                'price_unit': item.name.list_price,
                                'product_id': item.name.id,
                                'product_uom_id': item.name.uom_id and item.name.uom_id.id or False,
                                'sequence': sequence,
                            }))

            # Create Invoice lines for Labs
            if acc.labtest_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Tests',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))

                for lab in acc.labtest_line:
                    lab_test_name = lab.test_type.name + ' (' + lab.name + ')'

                    invoice_lines.append((0, 0, {
                        'display_type': False,
                        'name': lab_test_name,
                        'price_unit': lab.test_type.test_charge,
                        'quantity': 1,
                        'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                            'uom.product_uom_unit').id or False,
                        'sequence': sequence,
                    }))

            # Create Invoice lines for Prescription
            if acc.prescription_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Medicines',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))

                for pres_line in acc.prescription_line:
                    if pres_line.prescription_line:
                        for pres in pres_line.prescription_line:
                            sequence += 1
                            invoice_lines.append((0, 0, {
                                'display_type': False,
                                'quantity': pres.qty,
                                'name': pres.name.product_id.name,
                                'product_id': pres.name.product_id.id,
                                'product_uom_id': pres.name.product_id.uom_id and pres.name.product_id.uom_id.id or False,
                                'price_unit': pres.name.product_id.list_price,
                                'sequence': sequence,
                            }))
                        pres_line.write({'state': 'Invoiced'})
        return invoice_lines

    def set_to_completed(self):
        if self.env.company.followup_feature:
            return {
                'name': _('Follow-Up Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'oeh.followup.appointment.wizard',
                'view_mode': 'form',
                'target': 'new'
            }
        return self.write({'state': 'Completed'})

    def unlink(self):
        # for appointment in self.filtered(lambda appointment: appointment.state not in ['Scheduled']):
        #     raise UserError(_('You can not delete an appointment which is not in "Scheduled" state !!'))
        return super(OeHealthAppointment, self).unlink()


# Prescription Management
class OeHealthPrescriptions(models.Model):
    _name = 'oeh.medical.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'portal.mixin']

    STATES = [
        ('Draft', 'Draft'),
        ('Invoiced', 'Invoiced'),
        ('Sent to Pharmacy', 'Sent to Pharmacy'),
    ]

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Prescription #', size=64, readonly=True, required=True, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('is_pharmacist', '=', False)],
                             help="Current primary care / family doctor", required=True, readonly=True,
                             states={'Draft': [('readonly', False)]}, default=_get_physician)
    pharmacy = fields.Many2one('oeh.medical.health.center.pharmacy', 'Pharmacy', readonly=True,
                               states={'Draft': [('readonly', False)]})
    date = fields.Datetime(string='Prescription Date', readonly=True, states={'Draft': [('readonly', False)]},
                           default=datetime.datetime.now())
    info = fields.Text(string='Prescription Notes', readonly=True, states={'Draft': [('readonly', False)]})
    prescription_line = fields.One2many('oeh.medical.prescription.line', 'prescription_id', string='Prescription Lines',
                                        readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection(STATES, 'State', readonly=True, default=lambda *a: 'Draft')
    appointment = fields.Many2one('oeh.medical.appointment', string='Appointment #')
    move_id = fields.Many2one('account.move', string='Invoice #')
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center",
                                  readonly=True, states={'Draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='patient.partner_id', string='Partner')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.uid)
    send_prescription_by_email = fields.Boolean(string='Send Prescription by email',
                                                compute='set_prescription_by_email_from_conf')

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.prescription')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.prescription'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            values = {
                'name': 'Prescriptions (' + str(company.name) + ')',
                'code': 'oeh.medical.prescription',
                'company_id': company.id,
                'prefix': 'PR',
                'padding': 4,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.prescription')
            health_prescription = models.Model.create(self, vals)
            return health_prescription
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.prescription')
            health_prescription = super(OeHealthPrescriptions, self).create(vals)
            return health_prescription

    def set_prescription_by_email_from_conf(self):
        for pres in self:
            if self.env.company.prescription_send_by_email:
                pres.send_prescription_by_email = True
            else:
                pres.send_prescription_by_email = False

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def action_prescription_invoice_create(self):
        res = {}
        for pres in self:
            invoice_lines = []
            default_journal = self._get_default_journal()

            if not default_journal:
                raise UserError(_('No accounting journal with type "Sale" defined !'))

            if pres.prescription_line:
                sequence_count = 1
                invoice_lines.append((0, 0, {
                    'name': 'Medicines',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence_count,
                }))

                for ps in pres.prescription_line:
                    # Create Invoice lines
                    sequence_count += 1
                    invoice_lines.append((0, 0, {
                        'display_type': False,
                        'quantity': ps.qty,
                        'name': ps.name.product_id.name,
                        'product_id': ps.name.product_id.id,
                        'product_uom_id': ps.name.product_id.uom_id.id,
                        'price_unit': ps.name.product_id.list_price,
                        'sequence': sequence_count,
                    }))

            # Create Invoice
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': pres.patient.partner_id.id,
                'patient': pres.patient.id,
                'invoice_date': datetime.datetime.now().date(),
                'date': datetime.datetime.now().date(),
                'ref': "Prescription # : " + pres.name,
                'prescription': pres.id,
                'invoice_line_ids': invoice_lines
            })
            if self.env.company.stock_deduction_method == 'invoice_create':
                invoice.oeh_process_inventories()
            res = self.write({'state': 'Invoiced', 'move_id': invoice.id})
            if self.env.company.followup_feature:
                return {
                    'name': _('Follow-Up Wizard'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'oeh.followup.prescription.wizard',
                    'view_mode': 'form',
                    'target': 'new'
                }
        return res

    def unlink(self):
        # for priscription in self.filtered(lambda priscription: priscription.state not in ['Draft']):
        #     raise UserError(_('You can not delete a prescription which is not in "Draft" state !!'))
        return super(OeHealthPrescriptions, self).unlink()

    def action_prescription_send_to_pharmacy(self):
        pharmacy_obj = self.env["oeh.medical.health.center.pharmacy.line"]
        pharmacy_line_obj = self.env["oeh.medical.health.center.pharmacy.prescription.line"]
        res = {}
        for pres in self:
            if not pres.pharmacy:
                raise UserError(_('No pharmacy selected !!'))
            else:
                curr_pres = {
                    'name': pres.id,
                    'patient': pres.patient.id,
                    'doctor': pres.doctor.id,
                    'pharmacy_id': pres.pharmacy.id,
                    'state': 'Draft',
                }
                pharmacy_id = pharmacy_obj.create(curr_pres)

                if pharmacy_id:
                    if pres.prescription_line:
                        for ps in pres.prescription_line:
                            # Create Prescription line
                            curr_pres_line = {
                                'name': ps.name.id,
                                'indication': ps.indication.id,
                                'price_unit': ps.name.product_id.list_price,
                                'qty': ps.qty,
                                'actual_qty': ps.qty,
                                'prescription_id': pharmacy_id.id,
                            }

                            pharmacy_line_obj.create(curr_pres_line)

                pres.write({'state': 'Sent to Pharmacy'})

        return True

    def print_patient_prescription(self):
        return self.env.ref('oehealth.action_oeh_medical_report_patient_prescriptions').report_action(self)

    def action_prescription_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('oehealth.oeh_email_template_prescription',
                                                                raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'oeh.medical.prescription', self.ids[0])
        ctx = {
            'default_model': 'oeh.medical.prescription',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': True,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        self.ensure_one()
        auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
        return self.get_portal_url(query_string='&%s' % auth_param)


class OeHealthPrescriptionLines(models.Model):
    _name = 'oeh.medical.prescription.line'
    _description = 'Prescription Lines'

    FREQUENCY_UNIT = [
        ('Seconds', 'Seconds'),
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('When Required', 'When Required'),
    ]

    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    prescription_id = fields.Many2one('oeh.medical.prescription', string='Prescription Reference', required=True,
                                      ondelete='cascade', index=True)
    name = fields.Many2one('oeh.medical.medicines', string='Medicines', help="Prescribed Medicines",
                           domain=[('medicament_type', '=', 'Medicine')], required=True)
    indication = fields.Many2one('oeh.medical.pathology', string='Indication',
                                 help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    dose = fields.Integer(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")
    dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route',
                                 help="HL7 or other standard drug administration route code.")
    dose_form = fields.Many2one('oeh.medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    qty = fields.Integer(string='x', help="Quantity of units (eg, 2 capsules) of the medicament",
                         default=lambda *a: 1.0)
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection(FREQUENCY_UNIT, 'Unit', index=True)
    admin_times = fields.Char(string='Admin hours', size=128,
                              help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18')
    duration = fields.Integer(string='Treatment duration')
    duration_period = fields.Selection(DURATION_UNIT, string='Treatment period',
                                       help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately",
                                       index=True)
    start_treatment = fields.Datetime(string='Start of treatment')
    end_treatment = fields.Datetime('End of treatment')
    info = fields.Text('Comment')
    patient = fields.Many2one('oeh.medical.patient', 'Patient', help="Patient Name")


# Vaccines Management
class OeHealthVaccines(models.Model):
    _name = 'oeh.medical.vaccines'
    _description = 'Vaccines'

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Many2one('oeh.medical.medicines', string='Vaccine', domain=[('medicament_type', '=', 'Vaccine')],
                           required=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True)
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('is_pharmacist', '=', False)],
                             help="Current primary care / family doctor", required=True, default=_get_physician)
    date = fields.Datetime(string='Date', required=True, default=datetime.datetime.now())
    institution = fields.Many2one('oeh.medical.health.center', string='Institution',
                                  help="Health Center where the patient is being or was vaccinated")
    dose = fields.Integer(string='Dose #', default=lambda *a: 1)
    info = fields.Text('Observation')

    @api.onchange('patient', 'name')
    def onchange_patient(self):
        res = {}
        if self.patient and self.name:
            dose = 0
            query = _("select max(dose) from oeh_medical_vaccines where patient=%s and name=%s") % (
            str(self.patient.id), str(self.name.id))
            self.env.cr.execute(query)
            val = self.env.cr.fetchone()
            if val and val[0]:
                dose = int(val[0]) + 1
            else:
                dose = 1
            self.dose = dose
        return res


class OeHealthTreatment(models.Model):
    _name = 'oeh.medical.treatment'
    _description = 'oeHealth Treatment Management'

    def _default_institution(self):
        return self.env['oeh.medical.health.center'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)

    name = fields.Char(string='Treatment #', readonly=True, required=True, default=lambda *a: '/')
    appointment = fields.Many2one('oeh.medical.appointment', string='Appointment #')
    patient = fields.Many2one('oeh.medical.patient', string='Patient')
    treatment_type_id = fields.Many2one('oeh.medical.treatment.type', string="Treatment Type")
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor')
    treatment_date = fields.Date('Treatment Date')
    treatment_items = fields.One2many('oeh.medical.treatment.lines', 'treatment_id', string='Treatment Items')
    other = fields.Text(string='Other Information')
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center",
                                  default=_default_institution)
    company_id = fields.Many2one('res.company', related='institution.company_id', string='Company')
    currency_id = fields.Many2one('res.currency', related='institution.company_id.currency_id', string='Currency')

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.treatment')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.treatment'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            values = {
                'name': 'Treatments (' + str(company.name) + ')',
                'code': 'oeh.medical.treatment',
                'company_id': company.id,
                'prefix': 'TR',
                'padding': 4,
            }
            self.env['ir.sequence'].sudo().create(values)
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.treatment')
            vals['name'] = sequence
            health_treatment = models.Model.create(self, vals)
            return health_treatment
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.treatment')
            health_treatment = super(OeHealthTreatment, self).create(vals)
            return health_treatment


class OeHealthTreatmentLines(models.Model):
    _name = 'oeh.medical.treatment.lines'
    _description = 'oeHealth Treatment Management'

    name = fields.Many2one('product.product', string='Item')
    treatment_price = fields.Float(string='Charge', related='name.list_price')
    other = fields.Text(string='Other Information')
    treatment_id = fields.Many2one('oeh.medical.treatment', string='Treatment')
    qty = fields.Float(string='Quantity', default=1.0)
    company_id = fields.Many2one('res.company', related='name.company_id', string='Company')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')


class OeHealthTreatmentTypes(models.Model):
    _name = 'oeh.medical.treatment.type'
    _description = 'oeHealth Treatment Types Management'

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Name')


class oeHealthProduct(models.Model):
    _inherit = 'product.template'

    MEDICAMENT_TYPE_NEW = [
        ('Medicine', 'Medicine'),
        ('Vaccine', 'Vaccine'),
        ('Treatment', 'Treatment')
    ]

    medicament_type = fields.Selection(MEDICAMENT_TYPE_NEW, string='Medicament Type')
    treatment_item = fields.Boolean(string='Treatment Item', default=False)
    treatment_type_id = fields.Many2one('oeh.medical.treatment.type', string="Treatment Type")
