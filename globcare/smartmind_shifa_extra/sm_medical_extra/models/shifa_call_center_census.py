from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class CallCenterCensus(models.Model):
    _name = 'sm.shifa.call.center.census'
    _description = 'Call Center Census'

    def _get_employee(self):
        """Return default employee value"""
        therapist_obj = self.env['hr.employee']
        print(self.env.uid)
        domain = [('user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    STATES = [
        ('call_center', 'Call Center'),
        ('operation_manager', 'Operation.M'),
        ('done', 'Done'),
    ]

    name = fields.Char('Reference', index=True, copy=False)

    state = fields.Selection(STATES, string='State', readonly=True, default=lambda *a: 'call_center')
    caller_name = fields.Char(string='Caller Name', required=True, readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})

    mobile = fields.Char(size=10, string='Mobile', readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    city = fields.Char(string='City', readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    address = fields.Char(string='Address', readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    comm_meth = fields.Selection([
        ('call', 'Call'),
        ('whatsapp', 'Whatsapp'),
    ], string='Comms. Meth.', readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    service_asked = fields.Char( readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    in_out = fields.Selection([
        ('in', 'In'),
        ('out', 'Out'),
    ], string='In\Out', readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})
    comment = fields.Text( readonly=True, states={'call_center': [('readonly', False)],'operation_manager': [('readonly', False)]})

    answer_inquiry = fields.Boolean()
    book_app = fields.Boolean()
    send_ope = fields.Boolean()
    can_pos_ref = fields.Boolean()

    hhc_app = fields.Boolean()
    hhc_app_id = fields.One2many('sm.shifa.hhc.appointment', 'call_center_census_id')

    phy_app = fields.Boolean()
    phy_app_id = fields.One2many('sm.shifa.physiotherapy.appointment', 'call_center_census_id')

    tele_app = fields.Boolean()
    tele_app_id = fields.One2many('oeh.medical.appointment', 'call_center_census_id')

    hvd_app = fields.Boolean()
    hvd_app_id = fields.One2many('sm.shifa.hvd.appointment', 'call_center_census_id')

    pcr_app = fields.Boolean()
    pcr_app_id = fields.One2many('sm.shifa.pcr.appointment', 'call_center_census_id')

    can_pos = fields.Boolean()
    can_pos_id = fields.One2many('sm.shifa.cancellation.refund', 'call_center_census_id')
    person_in_charge = fields.Many2one('hr.employee', string="Person in Charge", default=_get_employee)
    date = fields.Datetime(string="Date", default=lambda *a: datetime.now())
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'done':
                raise UserError(_("You can archive only if it done census"))
        return super().action_archive()


    def set_to_operation_manager(self):
        return self.write({'state': 'operation_manager'})

    def set_to_call_center(self):
        return self.write({'state': 'call_center'})

    def set_to_done(self):
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.call.center.census')
        return super(CallCenterCensus, self).create(vals)


class ShifaHHCAppointmentInherit(models.Model):
    _inherit = 'sm.shifa.hhc.appointment'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')


class ShifaPhysiotherapyAppointmenttInherit(models.Model):
    _inherit = 'sm.shifa.physiotherapy.appointment'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')


class ShifaTeleAppointmenttInherit(models.Model):
    _inherit = 'oeh.medical.appointment'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')


class ShifaHVDAppointmenttInherit(models.Model):
    _inherit = 'sm.shifa.hvd.appointment'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')


class ShifaPCRAppointmenttInherit(models.Model):
    _inherit = 'sm.shifa.pcr.appointment'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')


class ShifaCancellationRefundtInherit(models.Model):
    _inherit = 'sm.shifa.cancellation.refund'

    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')