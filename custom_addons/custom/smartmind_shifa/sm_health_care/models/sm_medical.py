from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class ShifaServices(models.Model):
    _name = 'sm.shifa.service'
    _description = 'Shifa Medical HHC Service'
    _inherits = {
        'product.product': 'product_id',
    }

    TYPE = [
        ('HHC', 'HHC Appointment'),
        ('PHY', 'Physiotherapy Appointments'),
        ('PCR', 'PCR Appointment'),
        ('FUPH', 'HHC Follow Up'),
        ('FUPP', 'Physiotherapy Follow Up'),
        ('L', 'Laboratory'),
        ('LP', 'Laboratory Package'),
        ('R', 'Radiology'),
        ('WBSDFC', 'Wound Care'),
        ('GCP', 'Geriatric Care Program'),
        ('MH', 'Men\'s Health'),
        ('IVFA', 'IV Fluids/Antibiotic'),
        ('IV', 'IV Vitamins'),
        ('SM', 'Sleep Medicine'),
        ('V', 'Muscular/Subcut/Vaccines  Injection'),
        ('Car', 'Caregiver'),
        ('Diab', 'Diabetic Care'),
        ('Tel', 'Telemedicine'),
        ('HVD', 'Home Visit Doctor'),
    ]

    PRODUCT_TYPE = [
        ('service', 'Service'),
        ('consu', 'Consumable'),
        ('storable', 'Storable Product'),
    ]

    def _compute_abbr(self):
        for ser in self:
            ser.abbreviation = self.get_abbreviation(ser.name)

    product_id = fields.Many2one('product.product', string='Related Product', required=True, ondelete='cascade',
                                 help='Product-related data of the hospital services')
    name_ar = fields.Char('Service Name (AR)')
    service_type = fields.Selection(TYPE, string='Service Type', required=True)
    type_code = fields.Char(string='Code', readonly=True)
    # for Accounting purposes
    abbreviation = fields.Char(compute=_compute_abbr, string='Abbreviation', readonly=True)
    responsible = fields.Many2one('oeh.medical.physician', string='Responsible',
                                  domain=[('role_type', 'in', ['HD', 'HHCD']), ('active', '=', True)])
    description_ar = fields.Text('Description (AR)')
    description_sale_ar = fields.Text('Sale Description (AR)')
    more_details = fields.Text('More Details')
    more_details_ar = fields.Text('More Details (Ar)')
    active = fields.Boolean('Active',  default=True)
    show = fields.Boolean('Show', default=True)
    mains_forms = fields.Many2one('sm.shifa.service.module', domain=[('type','=','main')], string='Service Module')
    # type = fields.Selection(PRODUCT_TYPE, string='Type', required=True, default='service')
    duration = fields.Integer()
    refund_percent = fields.Integer('Refund (%)')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Service name must be unique!')
    ]

    def get_abbreviation(self, sentence):
        sentence = sentence.replace('(', '').replace(')', '')
        # add first letter
        oupt = sentence[0]
        # iterate over string
        for i in range(1, len(sentence)):
            if sentence[i - 1] == ' ':
                # add letter next to space
                oupt += sentence[i]
        # uppercase oupt
        oupt = oupt.upper().replace(',', '').replace('/', '').replace('-', '').replace(' ', '')
        return oupt

    @api.model
    def create(self, vals):
        vals['type_code'] = vals['service_type']
        # vals['type'] = 'service'
        vals['purchase_ok'] = False
        service_count = self.env['product.product'].search_count([('name', '=', vals['name'])])
        if service_count > 0:
            raise UserError(_('Sorry, the name of this service is already found in database !'))
        else:
            return super(ShifaServices, self).create(vals)
    
    def write(self, vals):
        res = super(ShifaServices, self).write(vals)
        if 'list_price' in vals and vals['list_price'] > 0:
            services = self.env['sm.shifa.package.service'].sudo().search([('service','=',self.id)])
            for service in services:
                service.sudo().write({"service_price": vals['list_price']})
                service._calculate_package_price()
                service.sudo().product.write({"lst_price": service.package_price + service.discount_amount})
        return res

    @api.onchange('service_type')
    def _onchange_service_type(self):
        self.type_code = self.service_type

    def unlink(self):
        model_name = 'product.product'
        service_obj = self.env[model_name].sudo().search([('id', '=', self.product_id.id)], limit=1)
        service_obj.unlink()
        return super(ShifaServices, self).unlink()
    def open_product_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('product.product_normal_action_sell')
        action['domain'] = [('id', '=', self.product_id.id)]
        action.update({'context': {}})
        return action

class ShifaHHCAppointmentTeamPeriod(models.Model):
    _name = 'sm.shifa.team.period'
    _description = 'Shifa Team Period for HHC'
    _rec_name = 'period'

    TYPE = [
        ('N', 'Nurse'),
        ('MH', 'Man’s Health'),
        ('GCP', 'Geriatric Care Program'),
        ('SM', 'Sleep Medicine'),
        ('Car', 'Caregiver'),
        ('Diab', 'Diabetic Care'),
    ]

    PERIOD_TIME = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]
    # Array containing different days name
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    name = fields.Selection(PHY_DAY, string='Available Day(s)', required=False)
    day = fields.Char(string='Day')

    type = fields.Selection(TYPE, string='Type', required=True)
    date = fields.Date(string='Date', required=True, default=lambda *a: datetime.now())
    period = fields.Selection(PERIOD_TIME, string='Time Slot', required=True)
    team_no = fields.Integer(string='Team #')
    service_per_time = fields.Integer(string='Service Per Time')
    booking = fields.Integer(string='Booking #', compute="_compute_appointment_count", store=True)
    available = fields.Integer(string='Available', compute="_compute_available", store=True)

    # date get day name
    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            a = datetime.strptime(str(self.date), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            self.name = self.day

    @api.depends("team_no", "service_per_time", "booking")
    def _compute_available(self):
        for record in self:
            record.available = (record.team_no * record.service_per_time) - record.booking

    @api.depends("date", "period", "type")
    def _compute_appointment_count(self):
        appointment = self.env['sm.shifa.hhc.appointment']
        for rec in self:
            rec.booking = appointment.search_count([('appointment_date_only', '=', rec.date), ('period', '=', rec.period), ('type', '=', rec.type)])


class ShifaPhysiotherapyTeamPeriod(models.Model):
    _name = 'sm.shifa.team.period.physiotherapy'
    _description = 'Shifa Team Period for Physiotherapy'

    GENDER = [('Male', 'Male'), ('Female', 'Female')]

    PERIOD_TIME = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]
    # Array containing different days name
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    name = fields.Selection(PHY_DAY, string='Available Day(s)', required=False)
    day = fields.Char(string='Day')

    gender = fields.Selection(GENDER, string='Type', required=True)
    date = fields.Date(string='Date', required=True, default=lambda *a: datetime.now())
    period = fields.Selection(PERIOD_TIME, string='Time Slot', required=True)
    team_no = fields.Integer(string='Team #')
    service_per_time = fields.Integer(string='Service Per Time')
    booking = fields.Integer(string='Booking #', compute="_compute_appointment_count")
    available = fields.Integer(string='Available', compute="_compute_available")

    # date get day name
    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            a = datetime.strptime(str(self.date), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            self.name = self.day

    def name_get(self):
        result = []
        for record in self:
            # result.append((record.id, "{}".format(record.period)))
            result.append((record.id, "{} - {}".format(record.gender, record.period)))
            # result.append((record.id, "{} {}".format(record.date, record.period)))
        return result

    @api.depends("team_no", "service_per_time")
    def _compute_available(self):
        for record in self:
            total = record.team_no * record.service_per_time
            record.available = total - record.booking

    def _compute_appointment_count(self):
        appointment = self.env['sm.shifa.physiotherapy.appointment']
        for rec in self:
            rec.booking = appointment.search_count(
                [('appointment_date_only', '=', rec.date), ('period', '=', rec.period), ('gender', '=', rec.gender)])


class ShifaPCRAppointmentTeamPeriod(models.Model):
    _name = 'sm.shifa.team.period.pcr'
    _description = 'Shifa Team Period'

    HOURS = [
        ('8:00 AM - 9:00 AM', '8:00 AM - 9:00 AM'),
        ('9:00 AM - 10:00 AM', '9:00 AM - 10:00 AM'),
        ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
        ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
        ('2:00 PM - 3:00 PM', '2:00 PM - 3:00 PM'),
        ('3:00 PM - 4:00 PM', '3:00 PM - 4:00 PM'),
        ('4:00 PM - 5:00 PM', '4:00 PM - 5:00 PM'),
        ('5:00 PM - 6:00 PM', '5:00 PM - 6:00 PM'),
        ('6:00 PM - 7:00 PM', '6:00 PM - 7:00 PM'),
        ('7:00 PM - 8:00 PM', '7:00 PM - 8:00 PM'),
    ]
    # Array containing different days name
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    name = fields.Selection(PHY_DAY, string='Available Day(s)', required=False)
    day = fields.Char(string='Day')

    date = fields.Date(string='Date', required=True, default=lambda *a: datetime.now())
    # hour = fields.Selection(HOURS, string='Hour', required=True)
    hour = fields.Float(string='Time (HH:MM)', required=True)
    team_no = fields.Integer(string='Team #')
    service_per_time = fields.Integer(string='Service Per Time')
    booking = fields.Integer(string='Booking #', compute="_compute_appointment_count")
    available = fields.Integer(string='Available', compute="_compute_available")

    # date get day name
    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            a = datetime.strptime(str(self.date), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            self.name = self.day

    @api.depends("team_no", "service_per_time")
    def _compute_available(self):
        for record in self:
            total = record.team_no * record.service_per_time
            record.available = total - record.booking

    def _compute_appointment_count(self):
        appointment = self.env['sm.shifa.pcr.appointment']
        for rec in self:
            rec.booking = appointment.search_count(
                [('appointment_date_only', '=', rec.date), ('appointment_time', '=', str(rec.hour))])


class ShifaConsultancy(models.Model):
    _name = 'sm.shifa.consultancy'
    # _rec_name = "type"
    _inherits = {
        'product.product': 'product_id',
    }

    TYPE = [
        ('TD', 'Telemedicine Doctor'),
        ('HVD', 'Home Visit Doctor'),
    ]

    PRODUCT_TYPE = [
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('storable', 'Storable Product'),
    ]

    product_id = fields.Many2one('product.product', string='Related Product', required=True, ondelete='cascade')
    type = fields.Selection(PRODUCT_TYPE, string='Type', required=True, default='service')
    # tele_price = fields.Float(string='Tele Charge')
    # hv_price = fields.Float(string='HV Charge')

    # consultancy_for = fields.Selection(TYPE, string='Type', required=True)
    # list_price = fields.Float(string='Consultancy Charge')

    @api.model
    def create(self, vals):
        vals['type'] = 'service'
        vals['purchase_ok'] = False
        return super(ShifaConsultancy, self).create(vals)

    def unlink(self):
        model_name = 'product.product'
        service_obj = self.env[model_name].sudo().search([('id', '=', self.product_id.id)], limit=1)
        service_obj.unlink()
        return super(ShifaConsultancy, self).unlink()


class ServiceModule(models.Model):
    _name = 'sm.shifa.service.module'
    _description = 'Shifa Service Module'

    name = fields.Char()
    type = fields.Char()
    code = fields.Char()




