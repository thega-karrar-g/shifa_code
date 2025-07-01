from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class InstantPrescriptions(models.Model):
    _name = 'sm.shifa.instant.prescriptions'
    _description = 'Instant Prescriptions'

    Instant_pre_STATE = [
        ('ready', 'Ready'),
        # ('dispensed', 'Dispensed'),
        ('send', 'Send'),
    ]

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        # print(user_ids)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def _get_current_user(self):
        self.user_sign = self.env.user

    name = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(Instant_pre_STATE, string='State', readonly=True, default=lambda *a: 'ready')

    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=False,
                              states={'send': [('readonly', True)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=False,
                      states={'send': [('readonly', True)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=False,
                           states={'send': [('readonly', True)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'send': [('readonly', True)]}, related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'send': [('readonly', True)]}, related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'send': [('readonly', True)]}, related='patient.age')
    nationality = fields.Char(string='Nationality', readonly=False,
                              states={'send': [('readonly', True)]}, related='patient.nationality')
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'send': [('readonly', True)]}, related='patient.weight')

    doctor = fields.Many2one('oeh.medical.physician',domain=[('active', '=', True)],
                             readonly=False, states={'send': [('readonly', True)]}, default=_get_physician)

    inst_con = fields.Char(string='Inst', readonly=False, states={'send': [('readonly', True)]})
    date_time = fields.Datetime(string='Date', default=lambda *a: datetime.datetime.now(), readonly=False,
                                states={'send': [('readonly', True)]})
    pharmacy_chain = fields.Many2one('sm.shifa.pharmacy.chain', string='Pharmacy Chain', readonly=True,
                                     states={'ready': [('readonly', False)]})
    # pharmacy = fields.Many2one('sm./shifa.pharmacies', string='Pharmacy', readonly=False, states={'send': [('readonly', True)]})
    pharmacy = fields.Many2one('sm.shifa.pharmacies', string='Pharmacy', readonly=False,
                               states={'send': [('readonly', True)]})
    pharmacist = fields.Many2one('sm.shifa.pharmacist', string='Pharmacist', domain="[('pharmacy', '=', pharmacy)]",
                                 readonly=False, states={'send': [('readonly', True)]})
    # pharmacy_name = fields.Char(related='pharmacist.name', string='Pharmacy',  readonly=False, states={'send': [('readonly', True)]})

    diagnosis = fields.Many2one('oeh.medical.pathology', readonly=False, states={'send': [('readonly', True)]})
    diagnosis_yes_no = fields.Boolean(readonly=False, states={'send': [('readonly', True)]})
    diagnosis_add2 = fields.Many2one('oeh.medical.pathology', readonly=False, states={'send': [('readonly', True)]})
    diagnosis_yes_no_2 = fields.Boolean(readonly=False, states={'send': [('readonly', True)]})
    diagnosis_add3 = fields.Many2one('oeh.medical.pathology', readonly=False, states={'send': [('readonly', True)]})

    drug_allergy = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_know', 'Not know'),
    ], readonly=False, states={'send': [('readonly', True)]})
    drug_allergy_text = fields.Char(readonly=False, states={'send': [('readonly', True)]})

    inst_prescription_line = fields.One2many('sm.shifa.prescription.line', 'inst_prescription_extra_ids',
                                             )  # readonly=False,
    # states={'send': [('readonly', True)]}

    user_sign = fields.Many2one('res.users', compute='_get_current_user')

    other_prescription_1 = fields.Char(readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})
    other_prescription_1_done = fields.Boolean('it was dispensed', readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})
    other_prescription_2 = fields.Char(readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})
    other_prescription_2_done = fields.Boolean('it was dispensed', readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})
    other_prescription_3 = fields.Char(readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})
    other_prescription_3_done = fields.Boolean('it was dispensed', readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})

    recommendations = fields.Text(readonly=False, states={'send': [('readonly', True)], 'ready': [('readonly', True)]})

    done = fields.Boolean('Done')
    link = fields.Char(readonly=True)

    # consultancy requested by patient
    cunsultancy_requested = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                             string="Consultancy Requested by Patient",
                                             readonly=False,
                                             states={'send': [('readonly', True)]})
    cunsultancy_id = fields.Char(string="ID", readonly=False,
                                 states={'send': [('readonly', True)]})
    cunsultancy_name = fields.Char(string="Name", readonly=False,
                                   states={'send': [('readonly', True)]})
    cunsultancy_age = fields.Char(string="Age", readonly=False,
                                  states={'send': [('readonly', True)]})
    cunsultancy_sex = fields.Char(string="Sex", readonly=False,
                                  states={'send': [('readonly', True)]})
    weight = fields.Float('Weight(kg)', readonly=False,
                                  states={'send': [('readonly', True)]})

    @api.model
    def process_next_ready_dispensed_state(self):
        self.search([
            ('state', '=', 'ready'),
        ]).write({
            'state': 'send'
        })

    # def set_to_dispensed(self):
    #     return self.write({'state': 'dispensed'})

    def set_to_send(self):
        return self.write({'state': 'send'})

    def download_pdf(self):
        return self.env.ref('smartmind_shifa_extra.sm_shifa_medical_pharmacy_presc_report').report_action(self)

    # def download_pdf(self):
    #     therapist_obj = self.env['sm.shifa.prescription.line']
    #     domain = [('instant_prescriptions', '=', self.id)]
    #     pres_id = therapist_obj.search(domain)
    #     return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(pres_id)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('sm.shifa.instant.prescriptions')
        prescription_patient = super(InstantPrescriptions, self).create(vals)
        if prescription_patient:
            if not prescription_patient.name:
                prescription_patient.name = sequence
        return prescription_patient

    def name_generation(self):
        if self.name == 'New':
            self.name = self.env['ir.sequence'].next_by_code('sm.shifa.instant.prescriptions')

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))

    def action_send_email(self):
        '''
        This function opens a window to compose an email, with the email template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('smartmind_shifa_extra', 'instance_prescription_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sm.shifa.instant.prescriptions',
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

    def action_send_sms(self):
        my_model = self._name
        if self.patient.mobile:
            msg = "Your Instance prescription is in link %s." % (self.link)
            self.send_sms(self.patient.mobile, msg, my_model, self.id)


class ShifaInstPrescriptionLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    inst_prescription_extra_ids = fields.Many2one('sm.shifa.instant.prescriptions', 'inst_prescription_line',
                                                  ondelete='cascade', index=True)
    dispensed = fields.Boolean(string='Dispensed')
    pharmacy_medicines = fields.Many2one('sm.shifa.pharmacy.medicines')
    pharmacy_generic = fields.Text(string='Generic', related='pharmacy_medicines.generic_medicine', store=True)
