from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class ShifaConsent(models.Model):
    _name = 'sm.shifa.consent'
    _description = "Consent"

    STATES = [
        ('Draft', 'Draft'),
        ('Signature', 'Signature'),
        ('Done', 'Done'),
    ]
    Languages = [
        ('Arabic', 'Arabic'),
        ('English', 'English'),
    ]
    approval_E = [
        ('Agree', 'agree'),
        ('Refuse', 'refuse'),
    ]
    approval_A = [
        ('أوافق', 'أوافق'),
        ('أرفض', 'أرفض'),
    ]
    relation_p_E = [
        ('Patient', ', patient'),
        ('Son of patient', ', son of patient'),
        ('Daughter of patient', ', daughter of patient'),
        ('Parent of patient', ', parent of patient'),
        ('relative of patient', ', relative of patient'),
    ]
    relation_p_A = [
        ('المريض', '، المريض'),
        ('ابن المريض', '، ابن المريض'),
        ('بنت المريض', '، بنت المريض'),
        ('والدي المريض', '، والدي المريض'),
        ('قريب المريض', '، قريب المريض'),
    ]
    Types = [
        ('Vaccination', 'Vaccination'),
        ('Urinary Catheterization', 'Urinary Catheterization'),
        ('Photograph and Video Permission', 'Photograph and Video Permission'),
        ('Peripherally Inserted Central Catheter Care and Management', 'Peripherally Inserted Central Catheter Care and Management'),
        ('Testosterone Replacement Therapy', 'Testosterone Replacement Therapy'),
    ]

    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    name = fields.Char('Reference', index=True, copy=False,  default=lambda *a: '/')

    approval_E_list = fields.Selection(approval_E, readonly=False, states={'Done': [('readonly', True)]})
    approval_A_list = fields.Selection(approval_A, readonly=False, states={'Done': [('readonly', True)]})
    relation_p_E_list = fields.Selection(relation_p_E, readonly=False, states={'Done': [('readonly', True)]})
    relation_p_A_list = fields.Selection(relation_p_A, readonly=False, states={'Done': [('readonly', True)]})

    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True, states={'Draft': [('readonly', False)]})

    ssn = fields.Char(size=256, related='patient.ssn',  readonly=False, states={'Done': [('readonly', True)]})
    patient_weight = fields.Float(string='Weight(kg)', related='patient.weight',  readonly=False, states={'Done': [('readonly', True)]})
    age = fields.Char(string='Age', related='patient.age',  readonly=False, states={'Done': [('readonly', True)]})
    date = fields.Datetime(string="Date", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    p_name = fields.Char(readonly=True, states={'Draft': [('readonly', False)]})

    language = fields.Selection(Languages, string="Language", default='Arabic', readonly=True, states={'Draft': [('readonly', False)]})
    type = fields.Selection(Types, string="Type", readonly=True, states={'Draft': [('readonly', False)]})
    english_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    vaccination_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    urinary_catheterization_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    photograph_and_video_permission_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    peripherally_inserted_central_catheter_care_and_management_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    testosterone_replacement_therapy_show = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})

    person_name = fields.Char(readonly=False, states={'Done': [('readonly', True)]})
    patient_name = fields.Text(readonly=False, states={'Done': [('readonly', True)]})
    relationship = fields.Text(readonly=False, states={'Done': [('readonly', True)]})
    signature = fields.Binary(readonly=True, states={'Signature': [('readonly', False)]})

    Reinsertion_type = fields.Boolean(string="Reinsertion of intermittent indwelling Foley's Catheter", readonly=True, states={'Draft': [('readonly', False)]})
    In_and_out_catheterization = fields.Boolean(string="In and Out catheterization for urine analysis", readonly=True, states={'Draft': [('readonly', False)]} )
    PICC_d = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    PICC_f = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    PICC_a = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    other_list = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)]})
    other_choice = fields.Char(readonly=True, states={'Draft': [('readonly', False)]})
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'Done':
                raise UserError(_("You can archive only if it done consent"))
        return super().action_archive()
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.consent')
        return super(ShifaConsent, self).create(vals)

    def send_to_sign(self):
        return self.write({'state': 'Signature'})

    def set_to_done(self):
        return self.write({'state': 'Done'})

    def download_consent(self):
        return self.env.ref('smartmind_shifa_more.sm_shifa_content_report').report_action(self)

class Patient(models.Model):
    _inherit = 'oeh.medical.patient'
    consent_count = fields.Integer(compute="_compute_consent_count")

    def _compute_consent_count(self):
        for record in self:
            record['consent_count'] = self.env['sm.shifa.consent'].sudo().search_count([('patient','=',record.id)])


    def show_consent(self):
        consent = self.env['sm.shifa.consent'].sudo().search([('patient','=',self.id)])
        if consent:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Consents',
                'context': {'default_patient': self.id},
                'res_model': 'sm.shifa.consent',
                'view_mode': 'tree,form',
                'domain': [('id','in',consent.ids)]
            }