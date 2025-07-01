from odoo import models, fields, api
import datetime
import base64


class ShifaImageTest(models.Model):
    _inherit = "oeh.medical.imaging"

    IMAGING_STATE = [
        ('Draft', 'Draft'),
        ('Test In Progress', 'Test In Progress'),
        ('pdf_generate', 'Generate Report'),
        ('upload_result', 'Upload Result'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ]
    state = fields.Selection(IMAGING_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    image_document = fields.Binary(readonly=True, states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]}, string='Image test Result Document')
    analysis = fields.Text(string='Analysis', readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    conclusion = fields.Text(string='Conclusion', readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image1 = fields.Binary(string="Image 1", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image2 = fields.Binary(string="Image 2", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image3 = fields.Binary(string="Image 3", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image4 = fields.Binary(string="Image 4", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image5 = fields.Binary(string="Image 5", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
    image6 = fields.Binary(string="Image 6", readonly=True, states={'Call Center': [('readonly', False)],'Team': [('readonly', False)],'Test In Progress': [('readonly', False)]})
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

    requestor = fields.Many2one('oeh.medical.physician', string='Requested by', help="Doctor", required=True,
                                domain=[('role_type', 'in', ['HD', 'HHCD', 'TD']), ('active', '=', True)],
                                readonly=True, states={'Draft': [('readonly', False)]})
    radiologist = fields.Many2one('oeh.medical.physician', string='Radiologist', required=True,domain=[('active', '=', True)],
                                readonly=True, states={'Draft': [('readonly', False)]}, default=_get_physician)
    imaging_Request = fields.Many2one('sm.shifa.imaging.request', string='IR#', domain="[('patient','=',patient)]",
                                      readonly=True, states={'Draft': [('readonly', False)]})
    file = fields.Text(string="File", readonly=True,
                       states={'Test In Progress': [('readonly', False)], 'Draft': [('readonly', False)]})

    date_requested = fields.Datetime(string='Date requested', readonly=True, states={'Draft': [('readonly', False)]},
                                     related="imaging_Request.admission_date", store=True)
    link = fields.Char(readonly=True)
    attach = fields.Boolean()#readonly=True
    attachment_ids = fields.Many2many('ir.attachment', string="Results", states={'Done': [('readonly', True)]})
    attachment_count = fields.Integer(compute="_compute_attachment_count")

    def _compute_attachment_count(self):
        for record in self:
            record['attachment_count'] = len(record.attachment_ids)


    def _get_pdf_link(self):
        link = ""
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        # print("URL", str(attachment_url))
        attach_name = self.env['ir.attachment'].search(
            ['|', ('name', '=', str(self.name) + '.pdf'), ('res_model', '=', "sm.shifa.lab.request")])
        # print("attach name: ", str(attach_name))
        for att_obj in attach_name:
            if att_obj.name == str(self.name) + ".pdf":
                link = attachment_url + str(att_obj.access_token)
        return link

    def control_generate_link(self):
        reports = self.search([
                ('state', '=', 'pdf_generate')])
        # print(reports)
        if reports:
            for rep in reports:
                rep.link = rep._get_pdf_link()
                rep.write({'state': 'Done'})

    def set_to_upload(self):
        # Generate pdf report and save it in attchment module.
        report = self.env.ref('smartmind_shifa.sm_shifa_imaging_report_action')._render_qweb_pdf(
            self.id)[0]
        report = base64.b64encode(report)
        return self.write({'state': 'pdf_generate', 'date_analysis': datetime.datetime.now()})

    def set_to_done_upload(self):
        self.attach = True
        return self.write({'state': 'upload_result', 'date_analysis': datetime.datetime.now()})

    def set_to_done(self):
        return self.write({'state': 'Done'})

    def set_to_test(self):
        return self.write({'state': 'Test In Progress'})

    def set_to_cancel(self):
        return self.write({'state': 'Cancelled', 'date_analysis': datetime.datetime.now()})

    def download_pdf(self):
        return self.env.ref('smartmind_shifa.sm_shifa_imaging_report_action').report_action(self)

        # connect the patient details with appointment

    @api.onchange('imaging_Request')
    def _onchange_join_lab_Request(self):
        if self.imaging_Request:
            self.image_test_request = self.imaging_Request

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            # print(self.patient)

