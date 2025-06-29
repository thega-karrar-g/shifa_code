import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time
import pytz


class ShifaPhysician(models.Model):
    _inherit = "oeh.medical.physician"
    _description = "Shifa Doctor Customization"

    ROLE_TYPE = [
        ('HD', 'Head Doctor'),
        ('HHCD', 'HHC Doctor'),
        ('TD', 'Telemedicine Doctor'),
        ('HN', 'Head Nurse'),
        ('HP', 'Head Physiotherapist'),
        ('HHCN', 'HHC Nurse'),
        ('HHCP', 'HHC Physiotherapist'),
        ('LT', 'Lab Technician'),
        ('SW', 'Social Worker'),
        ('C', 'Caregiver'),
        ('HVD', 'Home Visit Doctor'),
        ('RT', 'Respiratory Therapist'),
        ('CD', 'Clinical Dietitian'),
        ('DE', 'Diabetic Educator'),
        ('HE', 'Health Educator'),
        ('FD', 'Freelance Doctor'),
    ]
    DOCTOR_TYPE = [
        ('GP', 'GP'),
        ('Specialist', 'Specialist'),
    ]
    STATES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    APPOINTMENT_TYPE = [
        ('Not on Weekly Schedule', 'Not on Weekly Schedule'),
        ('On Weekly Schedule', 'On Weekly Schedule'),
    ]

    state = fields.Selection(STATES, string='State', default=lambda *a: 'draft', readonly=True)
    consultancy_type = fields.Many2one('sm.shifa.consultancy', string='Tele-charge Type', readonly=True, states={
        'draft': [('readonly', False)]})  # , domain=[('consultancy_for', '=', 'Telemedicine')]
    tele_price = fields.Float(string='Tele Charge', readonly=True,
                              states={'draft': [('readonly', False)]}, related='consultancy_type.list_price')
    hv_consultancy_type = fields.Many2one('sm.shifa.consultancy', string='HV-Charge Type', readonly=True, states={
        'draft': [('readonly', False)]})
    hv_price = fields.Float(string='HV Charge', readonly=True,
                            states={'draft': [('readonly', False)]}, related='hv_consultancy_type.list_price')
    role_type = fields.Selection(ROLE_TYPE, string='Role Type', help="Type of Doctor Role", readonly=True,
                                 states={'draft': [('readonly', False)]})
    doctor_type = fields.Selection(DOCTOR_TYPE, string='Doctor Type', default=lambda *a: 'GP', readonly=True,
                                   states={'draft': [('readonly', False)]})
    experience_years = fields.Integer(string='Years of Experience', readonly=True,
                                      states={'draft': [('readonly', False)]})
    # Store data in English
    job = fields.Many2one('sm.shifa.job', string='Job Title', readonly=True, states={'draft': [('readonly', False)]})
    license = fields.Many2one('sm.shifa.jobs.license', string='Job Classification', readonly=True,
                              states={'draft': [('readonly', False)]})
    license_no = fields.Char('Medical License Number', readonly=True, states={'draft': [('readonly', False)]})
    employer = fields.Char(string='Employer', readonly=True,
                           states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    scientific_expertise = fields.Char(string='Scientific Expertise', readonly=True,
                                       states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    practical_expertise = fields.Char(string='Practical Expertise', readonly=True,
                                      states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    languages = fields.Many2many('sm.shifa.language', string='Languages', readonly=True,
                                 states={'draft': [('readonly', False)]})
    country = fields.Char(string='Country', readonly=True, states={'draft': [('readonly', False)]})
    show_in_mobile_app = fields.Boolean('Show in Mobile App', readonly=True,
                                        states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    xls_file = fields.Binary('File', readonly=True, states={'draft': [('readonly', False)]})
    dr_categories_mobile = fields.Selection(DOCTOR_TYPE, string="Dr's categories in Mobile App", readonly=True,
                                            states={'draft': [('readonly', False)]})

    def set_to_active(self):
        return self.write({'state': 'active'})

    def set_to_draft(self):
        return self.write({'state': 'draft'})

    def set_to_inactive(self):
        return self.write({'state': 'inactive'})

    def import_xls(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))
        for sheet in wb.sheets():
            for row in range(sheet.nrows):
                for col in range(sheet.ncols):
                    print(sheet.cell(row, col).value)

    # Store data in Arabic
    def _get_arabic_job(self):
        job_obj = self.env['sm.shifa.job'].search([])
        lst = []
        for j in job_obj:
            lst.append(j.name_ar)
        return lst

    speciality = fields.Many2one('oeh.medical.speciality', string='Specialty', help="Speciality Code")
    name_ar = fields.Char(string='Name (AR)', readonly=True, states={'draft': [('readonly', False)]})
    speciality_ar = fields.Char(related='speciality.name_ar', string='Specialty (AR)', readonly=True,
                                states={'draft': [('readonly', False)]})
    job_ar = fields.Char(related='job.name_ar', string='Job Title (AR)', readonly=True,
                         states={'draft': [('readonly', False)]})
    license_ar = fields.Char(related='license.name_ar', string='License Title (AR)', readonly=True,
                             states={'draft': [('readonly', False)]})
    employer_ar = fields.Char(string='Employer (AR)', readonly=True,
                              states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    scientific_expertise_ar = fields.Char(string='Scientific Expertise (AR)', readonly=True,
                                          states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    practical_expertise_ar = fields.Char(string='Practical Expertise (AR)', readonly=True,
                                         states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    country_ar = fields.Char(string='Country (AR)', readonly=True, states={'draft': [('readonly', False)]})
    mobile = fields.Char(string='Mobile')
    schedule_availability = fields.One2many('sm.shifa.physician.schedule', 'doctor', string='Medical staffs Schedule Availability')
    ssn = fields.Char(size=256, string='ID Number', unique=True, readonly=True,
       states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    # Riyadh dammam and Jeddah
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=True,
       states={'draft': [('readonly', False)], 'active': [('readonly', False)]})

    @api.onchange('mobile')
    def mobile_check(self):
        if self.mobile:
            if self.mobile[0:4] == '9665':
                # print(len(self.mobile))
                if str(len(self.mobile)) == '12':
                    pass
                else:
                    lenth = len(self.mobile)
                    raise ValidationError("mobile number is {} digits should be 12 digits".format(lenth))
            else:
                raise ValidationError(_("Invalid mobile number"))


    def _convert_utc_to_local(self, date):
        date_format = "%Y-%m-%d %H:%M:%S"
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        local_date = datetime.strftime(
            pytz.utc.localize(datetime.strptime(date.split('.')[0], date_format)).astimezone(local),
            date_format)
        return local_date

    def write(self, vals):
        return super(ShifaPhysician, self).write(vals)


class ShifaPhysicianUpperActions(models.Model):
    _inherit = "oeh.medical.physician"

    # Compute methods
    def _hvd_app_count(self):
        oe_apps = self.env['sm.shifa.hvd.appointment']
        for pa in self:
            # if pa.role_type == '':
            domain = [('doctor', '=', pa.id)]
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
            if pa.role_type in ['HN', 'HHCN', 'HE']:
                domain = [('nurse', '=', pa.id)]
            elif pa.role_type == 'HD':
                domain = [('head_doctor', '=', pa.id)]
            elif pa.role_type in ['HD', 'HHCD']:
                domain = [('doctor', '=', pa.id)]
            elif pa.role_type in ['HP', 'HHCP']:
                domain = [('physiotherapist', '=', pa.id)]
            elif pa.role_type == 'SW':
                domain = [('social_worker', '=', pa.id)]
            elif pa.role_type == 'DE':
                domain = [('diabetic_educator', '=', pa.id)]
            elif pa.role_type == 'CD':
                domain = [('clinical_dietitian', '=', pa.id)]
            elif pa.role_type == 'RT':
                domain = [('respiratory_therapist', '=', pa.id)]
            else:
                domain = [('doctor', '=', pa.id)]

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
            domain = [('physiotherapist', '=', pa.id)]
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
            domain = [('head_doctor', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.pcr_app_count = app_count
        return True

    # count appointments for current patient
    hvd_app_count = fields.Integer(compute=_hvd_app_count, string="HVD Appointments")
    hhc_app_count = fields.Integer(compute=_hhc_app_count, string="HHC Appointments")
    phy_app_count = fields.Integer(compute=_phy_app_count, string="Physiotherapy Appointments")
    pcr_app_count = fields.Integer(compute=_pcr_app_count, string="PCR Appointments")


class ShifaNotifyPhysician(models.Model):
    _inherit = "oeh.medical.physician"

    doctor_fcm_token = fields.Char('Doctor FCM Token')
    device_type = fields.Char('Device Type')


class ShifaPhysicianLines(models.Model):
    _inherit = "oeh.medical.physician.line"
    _description = "Shifa Information about doctor availability Customization"

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
    name = fields.Selection(PHY_DAY, string='Available Day(s)', required=False)
    date = fields.Date(string='Date', required=True)
    duration = fields.Integer(string='Duration(M)')
    day = fields.Char(string='Day')

    # date get day name
    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            a = datetime.strptime(str(self.date), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            self.name = self.day

    @api.model
    def create(self, vals):
        duration = vals.get('duration')
        if duration < 5:
            raise ValidationError(_("Sorry, you cannot make duration less than 5 minutes."))
        return super(ShifaPhysicianLines, self).create(vals)

    @api.model
    def write(self, vals):
        duration = vals.get('duration')
        if duration:
            if duration < 5:
                raise ValidationError(_("Sorry, you cannot make duration less than 5 minutes."))

        return super(ShifaPhysicianLines, self).write(vals)


class ShifaPhysicianSpeciality(models.Model):
    _inherit = "oeh.medical.speciality"
    _description = "Shifa Doctor Speciality"

    name = fields.Char(string='Specialty', size=128, help="ie, Addiction Psychiatry", required=True)
    name_ar = fields.Char(string='Specialty (AR)')

    _order = 'name'
    _sql_constraints = [
        ('code_uniq', 'unique (company_id,name)', 'The Medical Speciality code must be unique')]
