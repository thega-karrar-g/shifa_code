import logging
import math
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ShifaPackageService(models.Model):
    _name = 'sm.shifa.package.service'
    _description = 'Package Service'

    SERVICE_TYPE = [
        ('hhc', 'HHC'),
        ('physiotherapy', 'Physiotherapy'),
    ]

    @api.onchange('service_type')
    def _onchange_service_type(self):
        self.service = None
        if self.service_type == "hhc":
            return {'domain': {'service': [('service_type', 'in', ['FUPH'])]}}
        elif self.service_type == "physiotherapy":
            return {'domain': {'service': [('service_type', 'in', ['FUPP'])]}}
        else:
            return {'domain': {'service': [('service_type', '=', False)]}}

    # calculate discount value form the total services
    @api.depends('miscellaneous_price', 'discount_amount', 'no_of_session', 'service_price')
    def _calculate_discount_amount(self):
        for rec in self:
            rec.discount_amount = ((rec.service_price * rec.no_of_session) + (
                    rec.miscellaneous_price * rec.no_of_session)) * (rec.discount_percent / 100)

    # calculate total price after discount
    @api.depends('miscellaneous_price', 'discount_amount', 'no_of_session', 'service_price', 'discount_percent')
    def _calculate_package_price(self):
        for rec in self:
            rec._get_discount_percent()
            rec.package_price = (rec.service_price * rec.no_of_session) + (
                    rec.miscellaneous_price * rec.no_of_session) - rec.discount_amount

    # get price of service
    @api.onchange('service')
    def _get_service_price(self):
        for rec in self:
            rec.service_price = rec.service.list_price

    # calculate discount amount for service
    @api.depends('discount_percent', 'service_price', 'no_of_session', 'discount_percent', 'miscellaneous_price')
    def _get_discount_percent(self):
        for rec in self:
            rec.discount_amount = ((rec.service_price * rec.no_of_session) + (
                    rec.miscellaneous_price * rec.no_of_session)) * (rec.discount_percent / 100)

    def _get_default_hvf(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('code', '=', 'PHVF')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        if hvf:
            return hvf.id or False
        else:
            return False

    # get the price of home visit service
    @api.onchange('miscellaneous_charge')
    def _get_miscellaneous_price(self):
        for rec in self:
            rec.miscellaneous_price = rec.miscellaneous_charge.list_price

    # get session for package
    @api.onchange('no_of_session')
    def get_session(self):
        for rec in self:
            rec.session = rec.no_of_session

    # get discount percentage
    @api.onchange('discount_percent')
    def get_discount_percent(self):
        for rec in self:
            rec.discount = rec.discount_percent

    # Service Info
    serial_no = fields.Char(string='Reference #')

    name = fields.Char(string='Package Name', required=True)
    service_type = fields.Selection(SERVICE_TYPE, string="Service Type")
    service = fields.Many2one('sm.shifa.service', string='Service Name', required=True)

    no_of_session = fields.Integer(string='No of Session', required=True)
    discount_percent = fields.Float(string='Discount %', required=True, default=0)

    # Price Details
    service_price = fields.Float(string='Service Price', readonly=True, related=False,
                                 store=True)  # , related='service.list_price'
    miscellaneous_charge = fields.Many2one('sm.shifa.miscellaneous.charge.service', string='Other Charges Type',
                                           required=True, readonly=True, default=_get_default_hvf)
    miscellaneous_price = fields.Float(string='Home Visit Fee',
                                       readonly=True, default=1.0, related="miscellaneous_charge.lst_price",
                                       store=True)  # , related='miscellaneous_charge.list_price'
    session = fields.Integer(string='Session #', readonly=True)
    discount = fields.Float(string='Discount %', readonly=True, default=0)
    discount_amount = fields.Float(string='Discount Amount', readonly=True, default=0.0, compute=_get_discount_percent)
    package_price = fields.Float('Package Price', readonly=True, default=0, compute=_calculate_package_price)
    description = fields.Text('Description')
    # ref for product package
    product_id = fields.Many2one('product.template', string='Product Template')
    product = fields.Many2one('product.product', string='Product')
    # archive feature
    active = fields.Boolean('Archive', default=True)
    refund_percent = fields.Float('Refund(%)',default=100,required=True)

    def generate_next_serial_no(self):
        model_name = 'sm.shifa.package.service'
        count = self.env[model_name].sudo().search_count([])
        next_serial_no = f"Pack-{count + 1:08}"
        return next_serial_no

    @api.model
    def create(self, vals):
        vals['serial_no'] = self.generate_next_serial_no()
        package = super(ShifaPackageService, self).create(vals)
        package.service_price = package.service.list_price
        self.create_product(package)
        return package

    # init:create product for package and get values from setting
    def create_product(self, package):
        ic = self.env['ir.config_parameter'].sudo()
        product_type = ic.get_param('smartmind_odoo.product_type')
        product_categ_id = ic.get_param('smartmind_odoo.product_categ_id')
        property_account_income_id = ic.get_param('smartmind_odoo.property_account_income_id')

        if product_type and product_categ_id and property_account_income_id:
            package.product = self.env['product.product'].create({
                "name": package.name,
                "type": product_type,
                "list_price": package.package_price + package.discount_amount,
                "purchase_ok": False,
                "taxes_id": False,
                "categ_id": product_categ_id,
                "property_account_income_id": int(property_account_income_id),
            }).id
        else:
            raise UserError(_(' you should add product package settings first '))

    # open product template form
    def open_product_template_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.product_template_action_product')
        action['domain'] = [('id', '=', self.product_id.id)]
        action.update({'context': {}})
        return action

    def open_product_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('product.product_normal_action_sell')
        action['domain'] = [('id', '=', self.product.id)]
        action.update({'context': {}})
        return action


class ShifaAppointmentsPackages(models.Model):
    _name = 'sm.shifa.package.appointments'
    _description = 'Package Service Appointments'
    _rec_name = 'serial_no'

    SERVICE_TYPE = [
        ('hhc', 'HHC'),
        ('physiotherapy', 'Physiotherapy'),
    ]
    PAY_THRU = [
        ('pending', 'Free Service'),
        ('package', 'Package'),
        ('aggregator_package', 'Aggregator Package'),
    ]

    PACKAGE_STATES = [
        ('draft', 'Draft'),
        ('send', 'Send for payment'),
        ('schedule', 'Schedule'),
        ('generated', 'Generated'),
        ('cancel', 'Cancelled'),

    ]

    PERIOD_TIME = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]
    GENDER = [('Male', 'Male'), ('Female', 'Female')]

    DAYS = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    # get the price of home visit service
    @api.depends('package')
    def _get_home_visit_price(self):
        for rec in self:
            rec.home_visit_fee = rec.package.miscellaneous_price

    def unlink(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError("You can only delete cancelled packages!")

        return super().unlink()

    # get price of service
    @api.depends('package')
    def _get_service_price(self):
        for rec in self:
            rec.service_price = rec.package.service_price

    # get service name
    @api.depends('package.service.name')
    def _get_service_name(self):
        for rec in self:
            rec.service = rec.package.service.name

    # get package sessins
    @api.depends('package.session')
    def _get_session(self):
        for rec in self:
            rec.session = rec.package.session

    # get package discount
    @api.depends('package', 'admin_discount', 'service_price', 'session', 'home_visit_fee')
    def _get_discount(self):
        for rec in self:
            rec.discount = rec.package.discount
        if rec.admin_discount:
            rec.discount_amount = ((rec.service_price * rec.session) + (
                    rec.home_visit_fee * rec.session)) * (rec.admin_discount / 100)
        else:
            rec.discount_amount = rec.package.discount_amount

    # get tax amount
    @api.depends('service_price', 'session', 'home_visit_fee', 'discount_amount', 'pay_thru')
    def _calculate_tax(self):
        for rec in self:
            rec.tax = 0
            if rec.pay_thru == 'package':
                if rec.patient.ksa_nationality == 'KSA':
                    rec.tax = 0
                else:
                    rec.tax = ((rec.service_price * rec.session) + (
                            rec.home_visit_fee * rec.session)) * 0.15
            else:
                rec.tax = ((rec.service_price * rec.session) + (
                        rec.home_visit_fee * rec.session)) * 0.15

    # total price with tax
    @api.depends('service_price', 'session', 'discount_amount', 'home_visit_fee', 'tax')
    def _calculate_total_amount(self):
        for rec in self:
            rec.amount_payable = (rec.service_price * rec.session) + (
                    rec.home_visit_fee * rec.session) + rec.tax - rec.discount_amount

    # get service type from package
    @api.depends('package.service_type')
    def _get_service_type(self):
        for rec in self:
            rec.service_type = rec.package.service_type

    serial_no = fields.Char(string='Reference #')

    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=False,
                              states={'generated': [('readonly', True)], 'send': [('readonly', True)],
                                      'schedule': [('readonly', True)], 'cancel': [('readonly', True)]})
    ssn = fields.Char(string='ID Number', readonly=True, related='patient.ssn')

    # package info
    date = fields.Date(string='Date', required=True, default=datetime.now(), readonly=False,
                       states={'generated': [('readonly', True)], 'send': [('readonly', True)],
                               'schedule': [('readonly', True)], 'cancel': [('readonly', True)]})
    package = fields.Many2one('sm.shifa.package.service', string='Package Service', required=True, readonly=False,
                              states={'generated': [('readonly', True)], 'send': [('readonly', True)],
                                      'schedule': [('readonly', True)], 'cancel': [('readonly', True)]})
    service = fields.Char(string='Service Name', readonly=True, compute=_get_service_name)
    service_price = fields.Float(string='Service Price', readonly=True, compute=_get_service_price)
    home_visit_fee = fields.Float(string='Home Visit Fee', readonly=True, compute=_get_home_visit_price)
    service_type = fields.Selection(SERVICE_TYPE, string="Service Type", readonly=True, compute=_get_service_type)

    session = fields.Integer(string='Session #', readonly=True, compute=_get_session)
    admin_discount = fields.Float(string='Admin Discount', copy=False, default=0, readonly=False,
                                  states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    discount = fields.Float(string='Discount %', readonly=True, compute=_get_discount, store=True)
    discount_amount = fields.Float(string='Discount Amount', readonly=True, compute=_get_discount, store=True)
    tax = fields.Float('VAT(+) 15%', readonly=True, compute=_calculate_tax)
    amount_payable = fields.Float('Amount Payable', readonly=True, compute=_calculate_total_amount)
    pro_pending = fields.Boolean(string="Pro. Free Service")

    # Appointment Info
    period = fields.Selection(PERIOD_TIME, string='Period', required=True, readonly=False,
                              states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    gender = fields.Selection(GENDER, string='Type', readonly=False,
                              states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    start_date = fields.Date(string='Start Date', required=True, readonly=False,
                             states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})

    start_day = fields.Selection(DAYS, string='Day', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)

    is_saturday = fields.Boolean(string='Saturday', readonly=False,
                                 states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_sunday = fields.Boolean(string='Sunday', readonly=False,
                               states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_monday = fields.Boolean(string='Monday', readonly=False,
                               states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_tuesday = fields.Boolean(string='Tuesday', readonly=False,
                                states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_wednesday = fields.Boolean(string='Wednesday', readonly=False,
                                  states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_thursday = fields.Boolean(string='Thursday', readonly=False,
                                 states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    is_friday = fields.Boolean(string='Friday', readonly=False,
                               states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})

    hhc_appointment_lines = fields.One2many('sm.shifa.hhc.appointment', 'appointment_package',
                                            states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]},
                                            string='HHC Appointment #', readonly=True)

    physiotherapy_appointment_lines = fields.One2many('sm.shifa.physiotherapy.appointment', 'appointment_package',
                                                      states={'generated': [('readonly', True)],
                                                              'cancel': [('readonly', True)]},
                                                      string='Physiotherapy Appointment #', readonly=True)
    # Team Info
    clinician_1 = fields.Many2one('oeh.medical.physician', string='Nurse', readonly=False,
                                  domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)],
                                  states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    timeslot = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot',
                               domain="[('date', '=', start_date), ('is_available', '=', True), ('physician_id', '=', clinician_1)]",
                               readonly=False,
                               states={'generated': [('readonly', False)], 'cancel': [('readonly', True)]})
    clinician_2 = fields.Many2one('oeh.medical.physician', string='Doctor', readonly=False,
                                  domain=[('role_type', 'in', ['HHCD', 'HD']), ('active', '=', True)],
                                  states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    timeslot_doctor = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot',
                                      domain="[('physician_id', '=', clinician_2), ('date', '=', start_date), ('is_available', '=', True)]",
                                      readonly=False,
                                      states={'generated': [('readonly', False)], 'cancel': [('readonly', True)]})

    clinician_3 = fields.Many2one('oeh.medical.physician', string='Physiotherapist', readonly=False,
                                  domain=[('role_type', 'in', ['HP', 'HHCP']), ('active', '=', True)],
                                  states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    timeslot_phy = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot',
                                   domain="[('physician_id', '=', clinician_3), ('date', '=', start_date), ('is_available', '=', True)]",
                                   readonly=False,
                                   states={'generated': [('readonly', False)], 'cancel': [('readonly', True)]})
    # ('physician_id', '=', clinician_1.id),

    state = fields.Selection(PACKAGE_STATES, string='State', default='draft')
    order_id = fields.Many2one('sale.order', string='Order #')
    order_note = fields.Text(string="Terms and Conditions", readonly=False,
                             states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})

    pay_thru = fields.Selection(PAY_THRU, string='Pay made thru', readonly=False,
                                states={'generated': [('readonly', True)], 'send': [('readonly', True)],
                                        'schedule': [('readonly', True)], 'cancel': [('readonly', True)]}
                                , required=True)
    aggregator = fields.Many2one('sm.aggregator', string='Aggregator', readonly=False,
                                 states={'generated': [('readonly', True)], 'send': [('readonly', True)],
                                         'schedule': [('readonly', True)], 'cancel': [('readonly', True)]})
    move_id = fields.Many2one('account.move', string='account move', ondelete='restrict', copy=False)
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=False,
        states={'generated': [('readonly', True)], 'send': [('readonly', True)], 'schedule': [('readonly', True)],
                'cancel': [('readonly', True)]})
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)
    active = fields.Boolean('Archive', default=True)
    refund_req = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request')

    def create_refund_request(self):
        pay_values = {
            # 'patient': self.patient_id.id,
            'patient': self.patient.id,
            'state': 'Processed',
            'type': 'package',
            'reason': '',
            'payment_request_id': self.pay_req_id.id if self.pay_req_id else False,
            'package_id': self.id,
            'move_ids': [(6, 0, self.move_ids.ids)] if self.move_ids else [(5, 0, 0)]
        }
        refund_req = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        self.refund_req = refund_req.id

    def open_cancel_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_cancellation_refund_action')
        action['domain'] = [('package_id', '=', self.id)]
        action.update({'context': {}})
        return action

    def create_payment(self):
        pay_values = {
            'patient': self.patient.id,
            'type': 'package',
            'details': 'package appointment',
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': self.amount_payable,
            'package_id': self.id,
            'package_date': self.date,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        self.pay_req_id = pay_req.id

    move_ids = fields.One2many('account.move', 'package_id')
    cancellation_reason = fields.Char()

    def open_payment(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('id', '=', self.pay_req_id.id)]
        action.update({'context': {}})
        return action

    def _compute_hhc_count(self):
        appointment = self.env['sm.shifa.hhc.appointment']
        for rec in self:
            domain = [('appointment_package', '=', rec.id)]
            app_ids = appointment.search(domain)
            apps = appointment.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            rec.hhc_apt_count = app_count
        return True

    hhc_apt_count = fields.Integer(compute=_compute_hhc_count, string="HHC Appointments")

    def _compute_physio_count(self):
        appointment = self.env['sm.shifa.physiotherapy.appointment']
        for rec in self:
            domain = [('appointment_package', '=', rec.id)]
            app_ids = appointment.search(domain)
            apps = appointment.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            rec.physio_apt_count = app_count
        return True

    physio_apt_count = fields.Integer(compute=_compute_physio_count, string="Physio Appointments")
    package_appointment_id = fields.Many2one('sm.shifa.package.appointments.multi')

    def get_appointment_time(self, timeslot):
        sch_time = False
        if timeslot:
            hm = timeslot.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
        return sch_time

    # method check selected days
    def check_selected_days(self, days):
        count = 0
        for rec in self:
            for key, value in days.items():
                if rec[key]:
                    count += 1
        if count:
            return True
        else:
            return False

    def set_to_generate(self):
        if not (self.is_saturday or self.is_sunday or self.is_monday or 
                self.is_tuesday or self.is_wednesday or self.is_thursday or self.is_friday):
            raise UserError("You should select at least one day!")
        if self.service_type == 'physiotherapy' and self.physiotherapy_appointment_lines:
            return
        if self.service_type == 'hhc' and self.hhc_appointment_lines:
            return
        dict = {
            'is_saturday': 'Saturday',
            'is_sunday': 'Sunday',
            'is_monday': 'Monday',
            'is_tuesday': 'Tuesday',
            'is_wednesday': 'Wednesday',
            'is_thursday': 'Thursday',
            'is_friday': 'Friday',
        }
        check_days = self.check_selected_days(dict)
        if check_days:
            for rec in self:
                unselected_dates = []
                for key, value in dict.items():
                    self._set_session_on_selected_day(rec[key], value, rec, unselected_dates)

                """
                generate lines for days in the loop but not selected,
                (if Friday is included in the loop and not selected in the patient profile, we have to generate an appointment for the next day selected (Saturday))
                """
                if unselected_dates:
                    # this is for the selected appointment type
                    if self.service_type == 'physiotherapy':
                        appointment = 'sm.shifa.physiotherapy.appointment'
                    else:
                        appointment = 'sm.shifa.hhc.appointment'

                    # this function is to prevent creating missing sessions on missing dates
                    def get_date(real_date):
                        reverse_dict = {
                            'Saturday': 'is_saturday',
                            'Sunday': 'is_sunday',
                            'Monday': 'is_monday',
                            'Tuesday': 'is_tuesday',
                            'Wednesday': 'is_wednesday',
                            'Thursday': 'is_thursday',
                            'Friday': 'is_friday',
                        }
                        # for key, value in reverse_dict.items():
                        day = real_date.strftime("%A")
                        if not rec[reverse_dict[day]]:
                            real_date = real_date + timedelta(1)
                            return get_date(real_date)

                        return real_date

                    for date in unselected_dates:

                        last_appointment = self.env[appointment].sudo().search([
                            ('appointment_package', '=', rec.id),
                        ], limit=1, order='appointment_date_only desc')  # get last appointment date to start after it

                        if last_appointment:
                            next_appointment_date = last_appointment.appointment_date_only + timedelta(1)
                            real_date = get_date(next_appointment_date)
                            # fetch first date of day_to_be_generated after last_appointment_date
                            self._is_timeslot_available(rec.clinician_1, real_date, rec.timeslot.available_time)
                            self._is_timeslot_available(rec.clinician_2, real_date, rec.timeslot_doctor.available_time)
                            self._is_timeslot_available(rec.clinician_3, real_date, rec.timeslot_phy.available_time)
                            if rec.service_type == 'hhc':
                                hhc = self.create_hhc_appointment_line(real_date, real_date.strftime("%A"), rec)
                            else:
                                phy = self.create_physiotherapy_appointment_line(real_date, real_date.strftime("%A"),
                                                                                 rec)

                            rec.end_date = real_date  # need it after generation
        else:
            raise UserError(_('Select at least one Day for Generate Appointment'))

        # create invoice order
        if not self.package_appointment_id:
            if self.pay_thru != 'pending':
                self.create_invoice()
            self.notification(self.pay_req_id)
        self.write({'state': 'generated'})
        return True

    def set_to_payment(self):
        if not self.package_appointment_id and self.pay_thru == 'package':
            self.create_payment()
        if self.pay_thru == 'aggregator_package':
            self.write({'state': 'schedule'})
        else:
            self.write({'state': 'send'})

    def set_to_scheduling(self):
        if not self.package_appointment_id and self.pay_thru == 'package':
            self.notification(self.pay_req_id)
        self.write({'state': 'schedule'})

    def notification(self, payment_id):
        msg = "payment request is  [ %s ]" % (payment_id.state)
        msg_vals = {"message": msg, "title": "Payment Request", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('analytic_account_id', '=', self.env.user.analytic_account_id.id)
        ], limit=1)
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale')
            ], limit=1)
        return journal

    def get_invoice_lines(self):
        invoice_lines = []
        if self.pay_thru == 'package':
            if self.patient.ksa_nationality == 'KSA':
                tax = False
            else:
                company = self.env.user.company_id
                tax = company.account_sale_tax_id
        else:
            company = self.env.user.company_id
            tax = company.account_sale_tax_id

        for line in self:
            sequence = 1
            if line.service:
                sequence += 1
                invoice_lines.append(
                    (0, 0, {
                        'product_id': self.package.product.id,
                        'price_unit': (self.service_price * self.session) + (self.home_visit_fee * self.session),
                        'tax_ids': tax,
                        'sequence': sequence,

                    }))
        return invoice_lines

    def get_refund_lines(self):
        account = False
        refundable_hhc_appointment_lines = self.hhc_appointment_lines.filtered(
            lambda h: h.state not in ['visit_done', 'in_progress'])
        refundable_phy_appointment_lines = self.physiotherapy_appointment_lines.filtered(
            lambda h: h.state not in ['visit_done', 'in_progress'])
        if len(refundable_hhc_appointment_lines) > 0:
            session = len(refundable_hhc_appointment_lines)
            account = int(self.env['ir.config_parameter'].sudo().get_param('smartmind_odoo.refund_account_hhc_id'))
        elif len(refundable_phy_appointment_lines) > 0:
            session = len(refundable_phy_appointment_lines)
            account = int(self.env['ir.config_parameter'].sudo().get_param('smartmind_odoo.refund_account_phy_id'))
        else:
            raise UserError("There is nothing to cancel!")

        invoice_lines = []
        if self.pay_thru == 'package':
            if self.patient.ksa_nationality == 'KSA':
                tax = False
            else:
                company = self.env.user.company_id
                tax = company.account_sale_tax_id
        else:
            company = self.env.user.company_id
            tax = company.account_sale_tax_id

        sequence = 1
        if self.service:
            sequence += 1
            amount = (self.service_price * session) + (self.home_visit_fee * session)
            if self.package.refund_percent > 0:
                amount = amount * (self.package.refund_percent / 100)

            invoice_lines.append(
                (0, 0, {
                    'product_id': self.package.product.id,
                    'price_unit': amount,
                    'tax_ids': tax,
                    'sequence': sequence,
                }),
            )
            discount_lines = self.move_ids.filtered(lambda m: m.move_type == 'out_invoice').mapped(
                'invoice_line_ids').filtered(lambda l: not l.product_id and l.price_unit < 0)
            if discount_lines:
                for discount_line in discount_lines:
                    invoice_lines.append(
                        (0, 0, {
                            'price_unit': discount_line.price_unit,
                            'tax_ids': [(6, 0, discount_line.tax_ids)] if discount_line.tax_ids else False,
                            'sequence': sequence,
                            'account_id': discount_line.account_id.id,
                        })
                    )
        return invoice_lines

    def create_invoice(self):
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        invoice_lines = self.get_invoice_lines()
        #default_journal = self._get_default_journal()
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)  
        # Create Invoice
        if self.pay_thru == 'aggregator_package':
            partner = self.aggregator.partner_id.id
        else:
            partner = self.patient.partner_id.id
        if not self.move_id:
            vals = {
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': partner,
                'analytic_account_id': analytical_account_id,
                'patient': self.patient.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Package Appointment",
                'invoice_line_ids': invoice_lines,
                'package_id': self.id,
            }
            if self.discount or self.admin_discount:
                vals['discount_type'] = 'percentage'
                vals['discount_amount'] = self.admin_discount if self.admin_discount else self.discount
            invoice = self.env['account.move'].sudo().create(vals)
            invoice.action_post()
            # self.move_id = invoice

    def create_credit_note(self):
        invoice_lines = self.get_refund_lines()
        default_journal = self._get_default_journal()
        # Create Invoice
        if self.pay_thru == 'aggregator_package':
            partner = self.aggregator.partner_id.id
        else:
            partner = self.patient.partner_id.id

        ref = 'Package Appointment'
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice'):
            ref = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].name
        receivable_line = False
        vals = {
            'move_type': 'out_refund',
            'journal_id': default_journal.id,
            'partner_id': partner,
            'analytic_account_id': self.env.user.analytic_account_id.id,
            'patient': self.patient.id,
            'invoice_date': datetime.now().date(),
            'date': datetime.now().date(),
            'ref': ref,
            'invoice_line_ids': invoice_lines,
            'package_id': self.id,
        }

        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice'):
            vals['reversed_entry_id'] = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].id
            receivable_line = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].line_ids.filtered(
                lambda l: l.account_id.user_type_id.id == 5)

        credit_note = self.env['account.move'].sudo().create(vals)
        credit_note_line = credit_note.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
        credit_note.action_post()
        if receivable_line and credit_note_line:
            lines = receivable_line + credit_note_line
            lines.reconcile()

    def create_journal(self):
        session = 0
        refundable_hhc_appointment_lines = self.hhc_appointment_lines.filtered(
            lambda h: h.state not in ['visit_done', 'in_progress'])
        refundable_phy_appointment_lines = self.physiotherapy_appointment_lines.filtered(
            lambda h: h.state not in ['visit_done', 'in_progress'])

        if len(refundable_hhc_appointment_lines) > 0:
            session = len(refundable_hhc_appointment_lines)

        elif len(refundable_phy_appointment_lines) > 0:
            session = len(refundable_phy_appointment_lines)

        if session > 0:
            amount = session * (self.service_price + self.home_visit_fee)
            if self.package.refund_percent > 0:
                percent = 1 - (self.package.refund_percent / 100)
                amount = amount * percent

            ic = self.env['ir.config_parameter'].sudo()
            journal_id = int(ic.get_param('smartmind_odoo.journal_id'))
            debit_account_id = int(ic.get_param('smartmind_odoo.debit_account_id'))
            credit_account_id = int(ic.get_param('smartmind_odoo.credit_account_id'))
            credit_discount_account_id = int(ic.get_param('smartmind_odoo.credit_discount_id'))
            debit_discount_account_id = int(ic.get_param('smartmind_odoo.debit_discount_id'))
            if self.pay_thru == 'package':
                name = 'package'
            elif self.pay_thru == 'aggregator_package':
                name = 'Aggregator Package'
            if journal_id and credit_account_id and debit_account_id:
                credit_line_vals = {
                    'name': name or ' ',
                    'credit': amount,
                    'debit': 0,
                    'account_id': credit_account_id,
                }
                debit_line_vals = {
                    'name': name or ' ',
                    'credit': 0,
                    'debit': amount,
                    'account_id': debit_account_id,
                }

                done_sessions = len(
                    self.hhc_appointment_lines.filtered(lambda h: h.state in ['visit_done', 'in_progress']))
                if self.physiotherapy_appointment_lines:
                    done_sessions = len(self.physiotherapy_appointment_lines.filtered(
                        lambda h: h.state in ['visit_done', 'in_progress']))

                if self.hhc_appointment_lines:
                    discount_val = done_sessions * self.discount_amount / len(self.hhc_appointment_lines)
                if self.physiotherapy_appointment_lines:
                    discount_val = done_sessions * self.discount_amount / len(self.physiotherapy_appointment_lines)

                debit_discount_vals = {
                    'name': name + "Discount" or ' ',
                    'debit': discount_val,
                    'credit': 0,
                    'account_id': credit_discount_account_id,

                }
                credit_discount_vals = {
                    'name': name + "Discount" or ' ',
                    'debit': 0,
                    'credit': discount_val,
                    'account_id': debit_discount_account_id,
                }
                line_ids = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
                if discount_val > 0:
                    line_ids = [(0, 0, debit_line_vals), (0, 0, credit_line_vals),
                                (0, 0, debit_discount_vals), (0, 0, credit_discount_vals)]
                vals = {
                    'move_type': 'entry',
                    'patient': self.patient.id,
                    'ref': self.serial_no,
                    'journal_id': journal_id,
                    'line_ids': line_ids,
                    'package_id': self.id,
                }
                journal = self.env['account.move'].create(vals)
                journal.action_post()
            else:
                raise UserError(_('Set journal ,debit account and credit account from settings'))

    def _get_days_session(self, sat, sun, mon, tue, wed, thr, fri):
        count = 0
        if sat:
            count += 1
        if sun:
            count += 1
        if mon:
            count += 1
        if tue:
            count += 1
        if wed:
            count += 1
        if thr:
            count += 1
        if fri:
            count += 1
        return count

    def _set_session_on_selected_day(self, is_this_day, day, rec, unselected_dates):
        days_no = self._get_days_session(rec.is_saturday, rec.is_sunday, rec.is_monday, rec.is_tuesday,
                                         rec.is_wednesday, rec.is_thursday, rec.is_friday)
        marker = 6
        if rec.session >= 10:
            marker = 7
        elif rec.session > 4 and days_no > 2:
            marker = 8

        count = math.ceil(int((rec.session / days_no) * marker))
        start = 0
        phy = 0
        while start < rec.session:
            sch_date = rec.start_date + timedelta(start)
            start += 1
            if day == self.get_day(sch_date):
                if is_this_day:
                    self._is_timeslot_available(rec.clinician_1, sch_date, rec.timeslot.available_time)
                    self._is_timeslot_available(rec.clinician_2, sch_date, rec.timeslot_doctor.available_time)
                    self._is_timeslot_available(rec.clinician_3, sch_date, rec.timeslot_phy.available_time)
                    if rec.service_type == 'hhc':
                        hhc = self.create_hhc_appointment_line(sch_date, day, rec)
                    else:
                        phy = self.create_physiotherapy_appointment_line(sch_date, day, rec)

                else:
                    if sch_date not in unselected_dates:
                        unselected_dates.append(sch_date)

            rec.end_date = sch_date  # need it after generation

    def test_session_days(self, is_this_day, day_name, rec):
        days_no = self._get_days_session(rec.is_saturday, rec.is_sunday, rec.is_monday, rec.is_tuesday,
                                         rec.is_wednesday, rec.is_thursday, rec.is_friday)
        marker = 6
        if rec.session >= 10:
            marker = 7
        elif rec.session > 4 and days_no > 2:
            marker = 8

        count = math.ceil(int((rec.session / days_no) * marker))
        #print('count', str(count))
        if is_this_day:
            start = 0
            while start < count:
                sch_date = rec.start_date + timedelta(days=start)
                start = start + 1
                #if day_name == self.get_day(sch_date):  # and selected < rec.session
                    #print('day', self.get_day(sch_date))
                    #print('sch_date', sch_date)

            rec.end_date = sch_date

    def create_hhc_appointment_line(self, sch_date, day, rec):
        model_name = 'sm.shifa.hhc.appointment'
        values = {
            'patient': rec.patient.id,
            'ssn': rec.ssn,
            'appointment_date_only': sch_date,
            'appointment_day': day,
            'period': rec.period,
            'branch': rec.branch,
            'service_type_choice': 'followup',
            'service': rec.package.service.id,
            'service_price': rec.service_price,
            'miscellaneous_charge': self._get_miscellaneous_id(),
            'miscellaneous_price': rec.home_visit_fee,
            'discount': self.admin_discount if self.admin_discount else self.discount,
            'payment_made_through': rec.pay_thru,
            'pro_pending': True if rec.pay_thru == 'pending' else False,
            'nurse': rec.clinician_1.id,
            'doctor': rec.clinician_2.id,
            'physiotherapist': rec.clinician_3.id,
            'timeslot': rec.timeslot.id,
            'timeslot_doctor': rec.timeslot_doctor.id,
            'timeslot_phy': rec.timeslot_phy.id,
            'aggregator': rec.aggregator.id,
            'appointment_time': self.get_appointment_time(rec.timeslot.available_time),
            'appointment_package': rec.id,
            'state': 'team',
        }
        hhc = self.env[model_name].sudo().create(values)
        return hhc

    # open invoice
    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = ['|', ('id', '=', self.move_id.id), ('id', 'in', self.move_ids.ids),
                            ('state', '!=', 'cancel')]
        action.update({'context': {}})
        return action

    def create_physiotherapy_appointment_line(self, sch_date, day, rec):
        model_name = 'sm.shifa.physiotherapy.appointment'
        values = {
            'patient': rec.patient.id,
            'ssn': rec.ssn,
            'appointment_date_only': sch_date,
            'appointment_day': day,
            'period': rec.period,
            'branch': rec.branch,
            'gender': rec.gender,
            'service_type_choice': 'followup',
            'service': rec.package.service.id,
            'service_price': rec.service_price,
            'miscellaneous_charge': self._get_miscellaneous_id(),
            'miscellaneous_price': rec.home_visit_fee,
            'discount': self.admin_discount if self.admin_discount else self.discount,
            'payment_made_through': rec.pay_thru,
            'pro_pending': True if rec.pay_thru == 'pending' else False,
            'physiotherapist': rec.clinician_3.id,
            'timeslot': rec.timeslot_phy.id,
            'aggregator': rec.aggregator.id,
            'appointment_time': self.get_appointment_time(rec.timeslot_phy.available_time),
            'appointment_package': rec.id,
            'state': 'team',
        }
        phy = self.env[model_name].sudo().create(values)
        return phy

    def get_day_date(self, rec, i, day_name):
        sch_date = rec.start_date + timedelta(days=i)
        day = self.get_day(sch_date)
        # print('day', str(day))
        # print('day_name', str(day_name))
        if day == day_name:
            # print('newX sch_date', str(sch_date))
            return sch_date
        else:
            self.get_day_date(rec, i + 1, day_name)
            return sch_date

    def get_day(self, sch_date):
        if sch_date:
            a = datetime.strptime(str(sch_date), "%Y-%m-%d")
            return str(a.strftime("%A"))

    def _get_miscellaneous_id(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('code', '=', 'PHVF')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        if hvf:
            return hvf.id or False
        else:
            return 0

    def _is_timeslot_available(self, physician, date, available_time):
        model_name = 'sm.shifa.physician.schedule.timeslot'
        domain = [('physician_id', '=', physician.id), ('date', '=', date),
                  ('available_time', '=', available_time), ('is_available', '=', True)]
        count = self.env[model_name].sudo().search_count(domain)
        if count == 10000:
            raise ValidationError(
                'Please note that {0} has no timeslot on {1} {2}'.format(physician.name, date, available_time))

    @api.onchange('timeslot_doctor')
    def _get_doctor_match_timeslot(self):
        for rec in self:
            if rec.clinician_2:
                if rec.timeslot.available_time != rec.timeslot_doctor.available_time:
                    raise ValidationError("The timeslot must be the Same")
                # self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('timeslot_phy')
    def _get_physiotherapist_match_timeslot(self):
        for rec in self:
            if rec.clinician_1 and rec.clinician_3 and rec.package.service_type == 'hhc':
                if rec.timeslot.available_time != rec.timeslot_phy.available_time:
                    raise ValidationError("The timeslot must be the Same")

    # check admin discount
    @api.onchange('admin_discount')
    def _check_admin_discount(self):
        for rec in self:
            if rec.admin_discount < 0 or rec.admin_discount > 100:
                raise ValidationError("The Admin discount percentage more than 0% and less than 100% ")

    def generate_next_serial_no(self):
        model_name = 'sm.shifa.package.appointments'
        count = self.env[model_name].sudo().search_count([])
        next_serial_no = f"Pack-{count + 1:08}"
        return next_serial_no

    @api.model
    def create(self, vals):
        vals['serial_no'] = self.generate_next_serial_no()
        record = super(ShifaAppointmentsPackages, self).create(vals)
        channel = self.env['mail.channel'].sudo().search([('id', '=', 209)])
        if channel:
            if record.patient.display_name and record.package.name:
                body = 'NEW package created for ' + record.patient.display_name + ' for the package ' + record.package.name
                channel.sudo().message_post(body=body, author_id=self.env['res.users'].browse(2).partner_id.id,
                                            message_type="comment", subtype_xmlid="mail.mt_comment")
        return record

    @api.onchange('start_date')
    def _onchange_date(self):
        if self.start_date:
            a = datetime.strptime(str(self.start_date), "%Y-%m-%d")
            #print('day', str(a.strftime("%A")))
            self.start_day = str(a.strftime("%A"))

    def action_cancel(self):
        for rec in self:
            if rec.state in ['draft', 'send']:
                rec.sudo().write({"state": "cancel"})
                break

                done_hhc_appointment_lines = rec.hhc_appointment_lines.filtered(
                    lambda h: h.state in ['visit_done', 'in_progress'])
                done_phy_appointment_lines = rec.physiotherapy_appointment_lines.filtered(
                    lambda h: h.state in ['visit_done', 'in_progress'])

                if done_hhc_appointment_lines or done_phy_appointment_lines:
                    raise UserError("You cannot cancel a package if there is an appointment in progress or done!")
                # hhc appointment lines canceled
                if rec.hhc_appointment_lines:
                    for line in rec.hhc_appointment_lines:
                        line.set_to_canceled()
                #  physiotherapy appointment lines canceled
                if rec.physiotherapy_appointment_lines:
                    for line in rec.physiotherapy_appointment_lines:
                        line.set_to_canceled()
                rec.move_id.button_draft()
                rec.move_id.button_cancel()

                rec.sudo().write({"state": "cancel"})
        
    
    def cancel(self):
        ctx = {
            'form_view_ref': 'smartmind_shifa_more.sm_shifa_package_appointment_cancel',
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def action_cancel(self):
        for rec in self:
            for line in rec.hhc_appointment_lines.filtered(lambda h: h.state not in ['visit_done', 'in_progress']):
                line.set_to_canceled()

            for line in rec.physiotherapy_appointment_lines.filtered(
                    lambda h: h.state not in ['visit_done', 'in_progress']):
                line.set_to_canceled()

            if self.env.context.get('from_multi') or self.move_id or self.move_ids.filtered(lambda l: l.move_type == 'out_invoice'):
                rec.create_credit_note()
                rec.create_journal()
            if not self.env.context.get('from_package'):
                self.create_refund_request()
            rec.sudo().write({"state": "cancel"})

    def action_archive(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("You can archive only if it cancelled Packages"))
        return super().action_archive()


class ShifaHHCAppointment(models.Model):
    _inherit = 'sm.shifa.hhc.appointment'

    appointment_package = fields.Many2one('sm.shifa.package.appointments', string='Appointment Package', index=True,
                                          ondelete='cascade')


class ShifaPhysioAppointment(models.Model):
    _inherit = 'sm.shifa.physiotherapy.appointment'

    appointment_package = fields.Many2one('sm.shifa.package.appointments', string='Appointment Package',
                                          index=True, ondelete='cascade')


class AccountMove(models.Model):
    _inherit = 'account.move'

    package_id = fields.Many2one('sm.shifa.package.appointments', string='Appointment Package',
                                 index=True, ondelete='cascade')