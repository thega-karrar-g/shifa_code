import datetime
from odoo import models, fields, api, _
import uuid
from odoo.exceptions import UserError


class ShifaPhysicianNotification(models.Model):
    _name = "sm.physician.notification"
    _description = "Physician Admission follow up Notification"
    _rec_name = 'name'

    ADMISSION_STATES = [
        ('Start', 'Start'),
        ('Send', 'Send'),
        ('Done', 'Done'),
    ]

    def _get_nurse(self):
        """Return default stoma value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char('Reference', index=True, copy=False)

    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Start', readonly=True)
    # appointment register link
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Start': [('readonly', False)]})
    # nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse',  readonly=True, states={'Start': [('readonly', False)]},
    #                              domain=[('role_type', '=', ['HHCN', 'HN'])])
    # phy_name = fields.Many2one('oeh.medical.physician', string='Physiotherapist', readonly=True,
    #                              states={'Start': [('readonly', False)]}, domain=[('role_type', '=', ['HP', 'HHCP'])])

    requested_by = fields.Many2one('oeh.medical.physician', string='Requested By', readonly=True,
                                   states={'Start': [('readonly', False)]}, required=True,
                                   domain=[('role_type', '=', ['HHCN', 'HHCP', 'C']), ('active', '=', True)],
                                   default=_get_nurse)
    phy_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment',
                                      string='Physiotherapy-Appointments', readonly=True,
                                      states={'Start': [('readonly', False)]})
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')

    # patient info
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Start': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly='1')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')

    # Services Provided
    services_provided_o2 = fields.Boolean(string="Oxygen Dependent", readonly=True,
                                          states={'Start': [('readonly', False)]})
    services_provided_tpn = fields.Boolean(string="TPN", readonly=True, states={'Start': [('readonly', False)]})
    services_provided_drain_tube_mx = fields.Boolean(string="Drain Tube Mx", readonly=True,
                                                     states={'Start': [('readonly', False)]})
    services_provided_tracheostomy = fields.Boolean(string="Tracheostomy", readonly=True,
                                                    states={'Start': [('readonly', False)]})
    services_provided_stoma_care = fields.Boolean(string="Stoma Care", readonly=True,
                                                  states={'Start': [('readonly', False)]})
    services_provided_medication_manage = fields.Boolean(string="Medication Management", readonly=True,
                                                         states={'Start': [('readonly', False)]})
    services_provided_wound_care = fields.Boolean(string="Wound Care", readonly=True,
                                                  states={'Start': [('readonly', False)]})
    services_provided_pdg_tube = fields.Boolean(string="PEG Tube", readonly=True,
                                                states={'Start': [('readonly', False)]})
    services_provided_warfarin = fields.Boolean(string="Warfarin Stabilization", readonly=True,
                                                states={'Start': [('readonly', False)]})
    services_provided_pain_manage = fields.Boolean(string="Pain Management", readonly=True,
                                                   states={'Start': [('readonly', False)]})
    services_provided_inr_monitor = fields.Boolean(string="INR Monitoring", readonly=True,
                                                   states={'Start': [('readonly', False)]})
    services_provided_parenteral = fields.Boolean(string="Parenteral Antimicrobial", readonly=True,
                                                  states={'Start': [('readonly', False)]})
    services_provided_hydration_therapy = fields.Boolean(string="Hydration Therapy", readonly=True,
                                                         states={'Start': [('readonly', False)]})
    services_provided_prevention_pressure_ulcer = fields.Boolean(string="Prevention of Pressure Ulcer", readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    services_provided_indwelling_foley = fields.Boolean(string="Indwelling Foley Catheter", readonly=True,
                                                        states={'Start': [('readonly', False)]})
    services_provided_o2_via_nasal = fields.Boolean(string="O2 via nasal cannula", readonly=True,
                                                    states={'Start': [('readonly', False)]})
    services_provided_vac_therapy = fields.Boolean(string="VAC Therapy", readonly=True,
                                                   states={'Start': [('readonly', False)]})
    services_provided_ngt = fields.Boolean(string="NGT", readonly=True, states={'Start': [('readonly', False)]})
    services_provided_hypodermoclysis = fields.Boolean(string="Hypodermoclysis", readonly=True,
                                                       states={'Start': [('readonly', False)]})
    services_provided_other = fields.Boolean(string="Other", readonly=True, states={'Start': [('readonly', False)]})
    services_provided_other_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    # remark
    notification_remarks = fields.Text(string='Remarks', readonly=True, states={'Start': [('readonly', False)]})
    # image
    image = fields.Binary(readonly=True, states={'Start': [('readonly', False)]})
    add_image = fields.Boolean(string='Other Image', readonly=True, states={'Start': [('readonly', False)]})
    other_image = fields.Binary(readonly=True, states={'Start': [('readonly', False)]})
    # Head Department Comment
    comment = fields.Text(readonly=True, states={'Send': [('readonly', False)]})

    physician_admission_followup = fields.Many2one('sm.physician.admission.followup', string='Physician Follow Up',
                                                   ondelete='cascade')
    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Text', readonly=True)
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'Done':
                raise UserError(_("You can archive only if it done supervisor consultation"))
        return super().action_archive()

    # connect the patient details with appointment
    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            self.phy_appointment = None

    @api.onchange('phy_appointment')
    def _onchange_phy_appointment(self):
        if self.phy_appointment:
            self.patient = self.phy_appointment.patient
            self.hhc_appointment = None

    @api.onchange('services_provided_other')
    def _onchange_services_provided_other(self):
        if not self.services_provided_other == 'Other':
            self.services_provided_other_content = ''

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.physician.notification')
        return super(ShifaPhysicianNotification, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        self.create_jitsi_meeting()
        return self.write({'state': 'Send', 'start_date': datetime.datetime.now()})

    def create_jitsi_meeting(self):
        # server_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') #+ '/videocall'
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        modle = self.env['sm.physician.notification'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link

        modle.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')
