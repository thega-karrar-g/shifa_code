import base64
from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ShifaImagingRequest(models.Model):
    _name = 'sm.shifa.imaging.request'
    _description = 'Image Request'


    IMAGETEST_STATE = [
        ('Call Center', 'Call Center'),
        ('Team', 'Team'),
        ('Patient', 'Patient'),
        ('Done', 'Done'),
    ]
    IMAGING_NUMBER = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ]

    state = fields.Selection(IMAGETEST_STATE, string='State', readonly=True, default=lambda *a: 'Call Center')

    def _get_doctor(self):
        """Return default breast value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Call Center': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Call Center': [('readonly', False)]})
    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD Appointment', readonly=True,
                                      states={'Call Center': [('readonly', False)]})
    # tele_appointment = fields.Many2one('sm.telemedicine.appointment', string='Tele-Appointment', readonly=True,
    #                                    states={'Call Center': [('readonly', False)]})

    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'TD']), ('active', '=', True)],
                             readonly=True, states={'Call Center': [('readonly', False)]}, default=_get_doctor)

    admission_date = fields.Datetime(string='Date Requested', readonly='1', default=lambda *a: datetime.datetime.now())
    discharge_date = fields.Datetime(string='Date of the Analysis', readonly='1')

    imaging_number_test = fields.Selection(IMAGING_NUMBER, string='Number of Tests', default='1', readonly=True,
                                           states={'Call Center': [('readonly', False)]})

    imaging_name1 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})
    imaging_name2 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})
    imaging_name3 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})
    imaging_name4 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})
    imaging_name5 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})
    imaging_name6 = fields.Many2one('oeh.medical.imaging.test.type', string='Imaging Name', readonly=True,
                                    states={'Call Center': [('readonly', False)]})

    result_document_imaging1 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    result_document_imaging2 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    result_document_imaging3 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    result_document_imaging4 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    result_document_imaging5 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    result_document_imaging6 = fields.Binary(string='Result Document', readonly=True,
                                             states={'Call Center': [('readonly', False)]})
    image_test_show = fields.Boolean()
    image_test_ids = fields.One2many('oeh.medical.imaging', 'image_test_request', string='Image Test')
    image_req_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'image_test_request', string='Image Request Test',
                                             readonly=False,
                                             states={'Done': [('readonly', True)]})
    active = fields.Boolean('Active', default=True)
    link = fields.Char(readonly=True)

    def _get_pdf_link(self):
        link = ""
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        # print("URL", str(attachment_url))
        attach_name = self.env['ir.attachment'].search(
            ['|', ('name', '=', str(self.name) + '.pdf'), ('res_model', '=', "sm.shifa.imaging.request")])
        # print("attach name: ", str(attach_name))
        for att_obj in attach_name:
            if att_obj.name == str(self.name) + ".pdf":
                # print("access_token:", str(att_obj.access_token))
                # print("id:", str(att_obj.id))
                # print("name:", str(att_obj.name))
                link = attachment_url + str(att_obj.access_token)
        return link

    def control_generate_link(self):
        reports = self.search([
            ('state', 'in', ['Team', 'Patient']),
        ])
        if reports:
            for rep in reports:
                rep.link = rep._get_pdf_link()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.imaging.request')
        return super(ShifaImagingRequest, self).create(vals)

    def set_to_call_center(self):
        return self.write({'state': 'Call Center'})

    def set_to_upload(self):
        for rep in self:
            rep.link = rep._get_pdf_link()
        return self.write({'state': 'Done', 'discharge_date': datetime.datetime.now()})

    def set_to_patient(self):
        report = self.env.ref('smartmind_shifa.sm_shifa_report_imaging_request_action')._render_qweb_pdf(
            self.id)[0]
        report = base64.b64encode(report)
        return self.write({'state': 'Patient'})

    def set_to_team(self):
        report = self.env.ref('smartmind_shifa.sm_shifa_report_imaging_request_action')._render_qweb_pdf(
            self.id)[0]
        report = base64.b64encode(report)
        return self.write({'state': 'Team'})

    # def set_to_cancel(self):
    #     return self.write({'state': 'Draft'})

    # connect the patient details with appointment
    def download_pdf(self):
        return self.env.ref('smartmind_shifa.sm_shifa_report_imaging_request_action').report_action(self)

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            print(self.patient)
            self.hvd_appointment = None
            # self.tele_appointment = None

    @api.onchange('hvd_appointment')
    def _onchange_hvd_appointment(self):
        if self.hvd_appointment:
            self.patient = self.hvd_appointment.patient
            self.hhc_appointment = None
            # self.tele_appointment = None

    @api.onchange('appointment')
    def _onchange_tele_appointment(self):
        if self.appointment:
            self.patient = self.appointment.patient
            self.hhc_appointment = None
            self.hvd_appointment = None

    # @api.onchange('tele_appointment')
    # def _onchange_tele_appointment(self):
    #     if self.tele_appointment:
    #         self.patient = self.tele_appointment.patient
    #         self.hhc_appointment = None
    #         self.hvd_appointment = None


class ShifaImageTestInherit(models.Model):
    _inherit = 'oeh.medical.imaging'

    image_test_request = fields.Many2one('sm.shifa.imaging.request', string='Image Test', ondelete='cascade')


class ShifaImageRequestLine(models.Model):
    _name = 'sm.shifa.imaging.request.line'
    _description = 'Image Request line'

    imaging_department = fields.Many2one('oeh.medical.imagingtest.department', string='Test Type')
    test_type = fields.Many2one('oeh.medical.imaging.test.type', string='Procedure Description',
                                domain="[('imaging_department', '=', imaging_department)]", help="Imaging Test type")
    type_test = fields.Many2many('oeh.medical.imaging.test.type',
                                 relation='imaging_requests_test_types_rel',
                                 column1='type_test_id',
                                 column2='imaging_request_id', string='Procedure Description',
                                 domain="[('imaging_department', '=', imaging_department)]")

    image_test_request = fields.Many2one('sm.shifa.imaging.request', string='Image Requested Test', ondelete='cascade')

