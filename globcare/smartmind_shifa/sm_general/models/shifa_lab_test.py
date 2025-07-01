from odoo import models, fields, api
import datetime
import base64


class ShifaLabTest(models.Model):
    _inherit = "oeh.medical.lab.test"

    LABTEST_STATE = [
        ('Draft', 'Draft'),
        ('Test In Progress', 'Test In Progress'),
        ('upload_result', 'Upload Result'),
        ('pdf_generate', 'Generate Report'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ]
    state = fields.Selection(LABTEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    lab_document = fields.Binary(readonly=True,
                                 states={'Draft': [('readonly', False)], 'Test In Progress': [('readonly', False)]},
                                 string='Lab test Result '
                                        'Document')
    results = fields.Text(string='Results', readonly=True,
                          states={'Test In Progress': [('readonly', False)]})
    diagnosis = fields.Text(string='Diagnosis', readonly=True,
                            states={'Test In Progress': [('readonly', False)]})

    lab_Request = fields.Many2one('sm.shifa.lab.request', string='LR#', domain="[('patient','=',patient)]",
                                  readonly=True, states={'Draft': [('readonly', False)]})

    requestor_id = fields.Many2one('oeh.medical.physician', string='Requested By', required="1",
                                   domain=[('role_type', 'in', ['HD', 'HHCD', 'TD']), ('active', '=', True)],
                                   help="Doctor who requested the test", readonly=True,
                                   states={'Draft': [('readonly', False)]})
    lab_specialist = fields.Many2one('oeh.medical.physician', string='Lab Specialist', readonly=True, required="1",
                                domain=[('active', '=', True)],
                                states={'Draft': [('readonly', False)]})
    container = fields.Text(string="Container", readonly=True,
                            states={'Test In Progress': [('readonly', False)]})

    date_requested = fields.Datetime(string='Date requested', readonly=True, states={'Draft': [('readonly', False)]}, related="lab_Request.admission_date", store=True)
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
            ['|', ('name', '=', str(self.name) + '.pdf'), ('res_model', '=', "oeh.medical.lab.test")])
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
                ('state', '=', 'pdf_generate')])
        if reports:
            for rep in reports:
                rep.link = rep._get_pdf_link()
                rep.write({'state': 'Done'})

    @api.onchange('lab_Request')
    def _onchange_join_lab_Request(self):
        if self.lab_Request:
            self.lab_test_request = self.lab_Request

    #  this is for scenario of generate report
    def set_to_upload(self):
        # generate report and save it at attachment module
        report = self.env.ref('smartmind_shifa.sm_shifa_lab_test_report_action')._render_qweb_pdf(
            self.id)[0]
        report = base64.b64encode(report)
        return self.write({'state': 'pdf_generate', 'date_analysis': datetime.datetime.now()})

    def set_to_done_upload(self):
        self.attach = True
        return self.write({'state': 'upload_result', 'date_analysis': datetime.datetime.now()})

    def set_to_done(self):
        return self.write({'state': 'Done'})

    def download_pdf(self):
        return self.env.ref('smartmind_shifa.sm_shifa_lab_test_report_action').report_action(self)

    def set_to_test(self):
        return self.write({'state': 'Test In Progress'})

    def set_to_cancel(self):
        return self.write({'state': 'Cancelled', 'date_analysis': datetime.datetime.now()})

     # connect the patient details with appointment
    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            print(self.patient)

