import random
import logging
import string
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64

_logger = logging.getLogger(__name__)

class SmOTPUser(models.Model):
    """
        OTP model is used for check registration and log patient in app by using Send SMS
    """
    _name = 'sm.otp.user'
    _rec_name = 'name'
    STATUS = [
        ('draft', 'Draft'),
        ('register', 'Register'),
        ('block', 'Blocked')
    ]

    state = fields.Selection(STATUS, string='Status', readonly=True, copy=False,
                             default=lambda *a: 'draft')

    name = fields.Char(required=True)
    username = fields.Char('Username', unique=True)
    password = fields.Char('password')
    ssn = fields.Char(size=256, string='National ID Number', required=True, unique=True, search=True)
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
    ], string='Marital Status')
    blood_type = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Blood Type')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    image_1920 = fields.Binary(string='Image')
    image_512 = fields.Binary()

    dob = fields.Date(string='Date of Birth')
    code = fields.Char(string='Code', default=lambda *a: ''.join(random.choices(string.digits, k=4)))
    patient = fields.Many2one('oeh.medical.patient', string='Patient')
    street = fields.Char()
    city = fields.Char()
    ksa_nationality = fields.Selection([('KSA','Saudi'),('NON','Non-Saudi')])

    # create a patient for validation correct code
    def create_patient(self):
        vals = {
            "name": self.name,
            "mobile": self.mobile,
            "dob": self.dob,
            "patient_password": self.password,
            "patient_username": self.username,
            "ssn": self.ssn,
            "sex": 'Male' if self.sex == 'male' else 'Female',
            "marital_status": self.marital_status,
            "blood_type": self.blood_type,
            "email": self.email,
            "street": self.street,

        }
        patient_obj = self.env['oeh.medical.patient'].sudo().create(vals)
        patient_obj._change_nationality()
        country = self.env['res.country'].sudo().search([('code', '=', 'SA')], limit=1)
        patient_obj.country_id = country.id if patient_obj.ksa_nationality == 'KSA' else False
        patient_obj.patient_password = self.password
        if patient_obj:
            self.patient = patient_obj.id
            portal =self.env.ref('base.group_portal').id
            user = self.env['res.users'].sudo().search([('partner_id','=',patient_obj.partner_id.id)])
            if not user:
                user = self.env['res.users'].sudo().create({
                'partner_id': patient_obj.partner_id.id,
                'name': patient_obj.name,
                'login': patient_obj.patient_username,
                'password': patient_obj.patient_password,
                'groups_id': [(6, 0, [portal])],
                })


    # Regenerate the Code
    def generate_code(self):
        self.code = ''.join(random.choices(string.digits, k=4))
    # sms send code
    def send_code(self):
        if self.mobile and self.code:
            model = self._name
            msg = "Your code is %s" % (self.code)
            self.send_sms(self.mobile, msg, model, self.id)

    #   SMS gateway for sending SMS code
    def send_sms(self, mobile, msg, model, rec_id):
            gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
            if gatewayurl_id and gatewayurl_id.gateway_url:
                try:
                    self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
                except Exception as e:
                    _logger.error(e)
            else:
                raise ValidationError(_("The SMS Gateway is not configured"))
