import base64
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime
from werkzeug.urls import url_encode
import logging

_logger = logging.getLogger(__name__)


class ShifaPrescription(models.Model):
    _inherit = "oeh.medical.prescription"

    STATES = [
        ('Start', 'Start'),
        ('PDF Created', 'PDF Created'),
        ('send', 'Send'),
    ]

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    def _get_current_user(self):
        self.user_sign = self.env.user

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

    state = fields.Selection(STATES, 'State', readonly=True, default=lambda *a: 'Start')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Start': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('is_pharmacist', '=', False), ('active', '=', True)],
                             help="Current primary care / family doctor", required=True, readonly=True,
                             states={'Start': [('readonly', False)]}, default=_get_physician)
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Start': [('readonly', False)]})
    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD Appointment', readonly=True,
                                      states={'Start': [('readonly', False)]})

    appointment = fields.Many2one('oeh.medical.appointment', string='Tele-Appointment', readonly=True,
                                       states={'Start': [('readonly', False)]})
    # tele_appointment = fields.Many2one('sm.telemedicine.appointment', string='Tele-Appointment', readonly=True,
    #                                    states={'Start': [('readonly', False)]})
    # pdf_document = fields.Binary(readonly=True, states={'Start': [('readonly', False)]}, string='PDF Document')
    date = fields.Datetime(string='Date', readonly=True, states={'Start': [('readonly', False)]}, default=lambda *a: datetime.now())
    info = fields.Text(string='Prescription Notes', readonly=True, states={'Start': [('readonly', False)]})
    prescription_line = fields.One2many('sm.shifa.prescription.line', 'prescription_ids',
                                        string='Prescription Lines',
                                        readonly=True, states={'Start': [('readonly', False)]})
    user_sign = fields.Many2one('res.users', compute='_get_current_user')
    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    phy_admission = fields.Many2one('sm.shifa.physician.admission', string='phy-Adm',
                                    readonly=True, states={'Start': [('readonly', False)]},
                                    ondelete='cascade')
    phy_assessment = fields.Many2one('sm.shifa.physician.assessment', string='phy-Ass',
                                    readonly=True, states={'Start': [('readonly', False)]},
                                    ondelete='cascade')

    diagnosis_show = fields.Boolean(default=True)
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                            states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})

    # Allergies
    allergies_show = fields.Boolean()
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy', related='patient.has_drug_allergy', readonly=False, states={'PDF Created': [('readonly', True)]})
    drug_allergy = fields.Boolean(default=False, readonly=False, related='patient.drug_allergy')
    drug_allergy_content = fields.Char(readonly=False, states={'PDF Created': [('readonly', True)]},
                                       related='patient.drug_allergy_content')

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy', readonly=False, related='patient.has_food_allergy',  states={'PDF Created': [('readonly', True)]})
    food_allergy = fields.Boolean(default=False, readonly=False,states={'PDF Created': [('readonly', True)]}, related='patient.food_allergy')
    food_allergy_content = fields.Char(readonly=False, states={'PDF Created': [('readonly', True)]}, related='patient.food_allergy_content')

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy', related='patient.has_other_allergy', readonly=False, states={'PDF Created': [('readonly', True)]})
    other_allergy = fields.Boolean(default=False, readonly=False, states={'PDF Created': [('readonly', True)]}, related='patient.other_allergy')
    other_allergy_content = fields.Char(readonly=False, states={'PDF Created': [('readonly', True)]},
                                        related='patient.other_allergy_content')

    active = fields.Boolean('Active', default=True)

    user_id = fields.Many2one(
        'res.users', string='send user', index=True, tracking=2, default=lambda self: self.env.user)
    link = fields.Char(readonly=True)

    @api.model
    def create(self, vals):
        rec = super(ShifaPrescription, self).create(vals)
        rec.create_prescription_record()
        return rec

    def create_prescription_record(self):
        medication_profile_obj = self.env["sm.shifa.medication.profile"]
        patient = self.patient.id
        date = self.date
        for rec in self.prescription_line:
            medication_profile = medication_profile_obj.sudo().create({
                'patient': patient,
                'p_generic_name': rec.generic_name.id,
                'p_brand_medicine': rec.brand_medicine.id,
                'p_indication': rec.indication.id,
                'p_dose': rec.dose,
                'p_dose_unit': rec.dose_unit.id,
                'p_dose_form': rec.dose_form.id,
                'p_common_dosage': rec.common_dosage.id,
                'p_duration': rec.duration,
                'p_qty': rec.qty,
                'p_duration_period': rec.frequency_unit,
                'p_dose_route': rec.dose_route.id,
                'state_app': 'active',
                'pre_exter_type': 'prescribed',
                'comment': " ",
                'date': date
            })

    def download_pdf(self):
        #return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(self)
        attachment = self.env['ir.attachment'].sudo().search([('res_model','=','oeh.medical.prescription'),('res_id','=',self.id)],limit=1,order="id desc")
        if attachment:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
            }

    """def set_to_pdf_create(self):
        # print("this is created pdf")
        self.write({'state': 'PDF Created'})
        return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(self)"""
    
    def set_to_pdf_create(self):
        if not self.prescription_line:
            raise ValidationError("Please add allergies!")
        # print("this is created pdf")
        self.write({'state': 'PDF Created'})
        pdf_content = self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions')._render_qweb_pdf([self.id])
        attachment = self.env['ir.attachment'].sudo().search([('res_model','=','oeh.medical.prescription'),('res_id','=',self.id)])
        if not attachment:
            attachment = self.env['ir.attachment'].sudo().create({
                'datas': pdf_content,
                'res_model': 'oeh.medical.prescription',
                'res_id': self.id,
                'name': self.name + '.pdf',
            })
        return self.generate_link()
    



    def _get_pdf_link(self):
        link = ""
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        # print("URL", str(attachment_url))
        attach_name = self.env['ir.attachment'].search(
            ['|', ('name', '=', self.name + '.pdf'), ('res_model', '=', "oeh.medical.prescription")])
        # print("attach name: ", str(attach_name))
        for att_obj in attach_name:
            if att_obj.name == str(self.name) + ".pdf":
                # print("access_token:", str(att_obj.access_token))
                # print("id:", str(att_obj.id))
                # print("name:", str(att_obj.name))
                link = attachment_url + str(att_obj.access_token)
        return link

    def generate_link(self):
        self.state = 'send'
        self.link = self._get_pdf_link()

    def _reset_token_number_sequences(self):
        prescriptions = self.search([
            ('state', 'in', ('Start', 'PDF Created')),
        ])
        if prescriptions:
            for pres in prescriptions:
                # print("pres=%s"%pres)
                if pres.state == "Start":
                    pres.write({'state': 'PDF Created'})
                    report = self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions')._render_qweb_pdf(
                        pres.id)[0]
                    report = base64.b64encode(report)
                    # filename = pres.name + '.pdf'
                    # attachment = self.env['ir.attachment'].create({
                    #     'name': filename,
                    #     'type': 'binary',
                    #     'datas': base64.b64encode(report[0]),
                    #     'res_model': 'oeh.medical.prescription',
                    #     'res_id': pres.id,
                    #     'mimetype': 'application/x-pdf'
                    # })
                else:
                    pres.generate_link()

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=False):
        self.ensure_one()
        auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
        return self.get_portal_url(query_string='&%s' % auth_param)

    def action_send_sms(self):
        my_model = self._name
        # print(my_model)
        if self.patient.mobile:
            msg = "You can download Your prescription from: %s." % (self.link)
            # print(">>>>>>>>>>>>", msg)
            self.send_sms(self.patient.mobile, msg, my_model, self.id)

    def action_send_email(self):
        '''
        This function opens a window to compose an email, with the email template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('smartmind_shifa', 'patient_prescription_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'oeh.medical.prescription',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('drug_allergy', 'food_allergy', 'other_allergy')
    def get_selection(self):
        # print(self.drug_allergy)
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

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))