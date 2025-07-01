from datetime import timedelta, datetime
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SmartMindDoctorSchedule(models.Model):
    _name = "sm.shifa.physician.schedule"
    _description = "Medical staffs Schedule"
    _rec_name = 'doctor'

    SCHEDULED_STATES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
    ]

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

    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('active', '=', True)],
                             readonly=False, states={'generated': [('readonly', True)]}) # , default=_get_physician

    start_time = fields.Float(string='Start', default=8.0, readonly=False, states={'generated': [('readonly', True)]})
    end_time = fields.Float(string='End', default=14.0, readonly=False, states={'generated': [('readonly', True)]})
    duration = fields.Float(string='Duration (Minutes)', default=30, readonly=False,
                            states={'generated': [('readonly', True)]})

    is_saturday = fields.Boolean(string='Saturday', readonly=False, states={'generated': [('readonly', True)]})
    is_sunday = fields.Boolean(string='Sunday', readonly=False, states={'generated': [('readonly', True)]})
    is_monday = fields.Boolean(string='Monday', readonly=False, states={'generated': [('readonly', True)]})
    is_tuesday = fields.Boolean(string='Tuesday', readonly=False, states={'generated': [('readonly', True)]})
    is_wednesday = fields.Boolean(string='Wednesday', readonly=False, states={'generated': [('readonly', True)]})
    is_thursday = fields.Boolean(string='Thursday', readonly=False, states={'generated': [('readonly', True)]})
    is_friday = fields.Boolean(string='Friday', readonly=False, states={'generated': [('readonly', True)]})

    start_date = fields.Date(string='Start Date', readonly=False, states={'generated': [('readonly', True)]},
                             help="Schedule start date")
    end_date = fields.Date(string='End Date', readonly=False, states={'generated': [('readonly', True)]},
                           help="Schedule end date")
    available_lines = fields.One2many('sm.shifa.physician.schedule.line', 'schedule_id', string='Doctor Availability',
                                      readonly=False, states={'generated': [('readonly', True)]})
    state = fields.Selection(SCHEDULED_STATES, string='State', default='draft', readonly=False,
                             states={'generated': [('readonly', True)]})

    # @api.onchange('end_time')
    # def onchange_end_time(self):
    #     if self.end_time:
    #         if self.end_time <= self.start_time:
    #             raise ValidationError('Sorry, end time must be greater than start time')
    @api.constrains('end_time')
    def validate_end_time(self):
        """
        check if end time greater than start time or not.
        if end time not greater than start time, it will show validation message to user.
        :return: None
        """
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError('Sorry, end time must be greater than start time')

    @api.constrains('end_date')
    def validate_end_date(self):
        """
        check if end date greater than start date or not.
        if end date not greater than start date, it will show validation message to user.
        :return: None
        """
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError('Sorry, end date must be greater than start date')

    # @api.onchange('end_date')
    # def onchange_end_date(self):
    #     if self.end_date:
    #         if self.end_date <= self.start_date:
    #             raise ValidationError('Sorry, end date must be greater than start date')

    # def set_to_scheduled(self):
    #     for rec in self:
    #         d_duration = (rec.end_date - rec.start_date).days
    #         for i in range(d_duration):
    #             self.generate_schedule_lines(rec.is_saturday, 'Saturday', rec, i)
    #             self.generate_schedule_lines(rec.is_sunday, 'Sunday', rec, i)
    #             self.generate_schedule_lines(rec.is_monday, 'Monday', rec, i)
    #             self.generate_schedule_lines(rec.is_tuesday, 'Tuesday', rec, i)
    #             self.generate_schedule_lines(rec.is_wednesday, 'Wednesday', rec, i)
    #             self.generate_schedule_lines(rec.is_thursday, 'Thursday', rec, i)
    #             self.generate_schedule_lines(rec.is_friday, 'Friday', rec, i)
    #     self.write({'state': 'generated'})
    #     return True

    def set_to_scheduled(self):
        """
        generate all schedule lines between start and end dates
        :return: True
        """
        for rec in self:

            # this code is written by mostafa to optimize the script and remove the multiple loops
            dict = {
                'is_saturday': 'Saturday',
                'is_sunday': 'Sunday',
                'is_monday': 'Monday',
                'is_tuesday': 'Tuesday',
                'is_wednesday': 'Wednesday',
                'is_thursday': 'Thursday',
                'is_friday': 'Friday',
            }
            d_duration = (rec.end_date - rec.start_date).days
            for single_date in (rec.start_date + timedelta(n) for n in range(d_duration + 1)):
                for key, value in dict.items():
                    if rec[key] and single_date.strftime("%A") == value:
                        #print("No problem")
                        self.save_schedule_lines(single_date, self.get_day(single_date))

        self.write({'state': 'generated'})
        return True
    # def generate_schedule_lines(self, is_this_day, day_name, rec, i):
    #     if is_this_day:
    #         sch_date = self.get_day_date(rec, i, day_name)
    #         day = self.get_day(sch_date)
    #         if sch_date:
    #             self.save_schedule_lines(rec, sch_date, day)

    def save_schedule_lines(self, sch_date, day):
        model_line = 'sm.shifa.physician.schedule.line'
        count = self.env[model_line].sudo().search_count([('schedule_id', '=', self.id), ('date', '=', sch_date)])
        values = {'schedule_id': self.id, 'date': sch_date, 'day': day, 'duration': self.duration,
                  'start_time': self.start_time, 'end_time': self.end_time}
        if count > 0:
            self.env[model_line].sudo().write(values)
        else:
            self.env[model_line].sudo().create(values)
        self.generate_timeslot(self.id, self.doctor)

    def generate_timeslot(self, schedule_id, doctor):
        date_in_str = str(datetime.now()).split('.')[0]
        date_in_str_loc = self._convert_utc_to_local(date_in_str)
        today = datetime.strptime(str(date_in_str_loc), "%Y-%m-%d %H:%M:%S")
        today_date = today.strftime('%Y-%m-%d')
        today_time = today.strftime('%H:%M')

        schedule_list = self.env['sm.shifa.physician.schedule.line'].sudo().search([('schedule_id', '=', schedule_id)])
        if schedule_list:
            for sch in schedule_list:
                # Convert the schedule date to a formatted string
                sch_date = sch.date.strftime("%Y-%m-%d")
                # Calculate the number of hours between the start and end time
                hours = int(sch.end_time - sch.start_time)
                # Convert the start time to a formatted string
                str_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sch.start_time) * 60, 60))
                given_time = datetime.strptime(str_time, '%H:%M')
                lst = []  # List to store generated timeslots
                counter = 0
                if sch.duration > 0:
                    while counter < (60 * hours):
                        spilt = given_time + timedelta(minutes=counter)
                        spilt_time = spilt.strftime('%H:%M')
                        if sch_date >= today_date:
                            if sch_date == today_date:
                                if today_time <= spilt_time:
                                    self.save_timeslot(sch.id, doctor.id, sch_date, spilt_time)
                                    lst.append(spilt_time)
                            else:
                                self.save_timeslot(sch.id, doctor.id, sch_date, spilt_time)
                                lst.append(spilt_time)

                        counter += sch.duration

    def save_timeslot(self, schedule_line_id, physician_id, date, available_time):
        model_name = 'sm.shifa.physician.schedule.timeslot'
        domain = [('physician_id', '=', int(physician_id)), ('date', '=', date), ('available_time', '=', str(available_time))]
        count = self.env[model_name].sudo().search_count(domain)
        values = {'schedule_line_id': schedule_line_id, 'physician_id': int(physician_id), 'date': date, 'available_time': available_time}
        if count > 0:
            tm_obj = self.env[model_name].sudo().search(domain, limit=1)
            tm_obj.sudo().write(values)
        else:
            self.env[model_name].sudo().create(values)

    def remove_old_timeslot(self, doctor_id):
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
            ['|', ('physician_id', '=', int(doctor_id)), ('is_available', '=',True)])
        timeslot.sudo().unlink()

    def get_day(self, sch_date):
        if sch_date:
            a = datetime.strptime(str(sch_date), "%Y-%m-%d")
            return str(a.strftime("%A"))

    def get_day_date(self, rec, i, day_name):
        sch_date = rec.start_date + timedelta(days=i)
        day = self.get_day(sch_date)
        if day == day_name:
            return sch_date

    def _convert_utc_to_local(self, date):
        date_format = "%Y-%m-%d %H:%M:%S"
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        local_date = datetime.strftime(
            pytz.utc.localize(datetime.strptime(date.split('.')[0], date_format)).astimezone(local),
            date_format)
        return local_date

    def set_to_timeslot(self):
        self.generate_timeslot(19, 1)

    # def unlink(self):
    #     for rec in self:
    #         timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
    #             [('physician_id', '=', int(rec.doctor.id))])
    #         timeslot.sudo().unlink()
    #         sch_lines = self.env['sm.shifa.physician.schedule.line'].sudo().search([('schedule_id', '=', int(rec.id))])
    #         sch_lines.sudo().unlink()
    #     return super(SmartMindDoctorSchedule, self).unlink()

    @api.model
    def create(self, vals):
        # VI We comment the following as recommendation from Dr. Najeeb
        # doctor_count = self.env['sm.shifa.physician.schedule'].search_count([('doctor', '=', vals.get('doctor'))])
        # if doctor_count > 0:
        #     raise UserError(_('You cannot add two schedules to the same doctor, remove old one first'))
        return super(SmartMindDoctorSchedule, self).create(vals)


class SmartMindDoctorScheduleLines(models.Model):
    _name = "sm.shifa.physician.schedule.line"
    _description = "Medical staffs Schedule Line"

    WEEK_DAYS = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    schedule_id = fields.Many2one('sm.shifa.physician.schedule', string='Medical staffs Schedule', index=True,
                                  ondelete='cascade')
    date = fields.Date(string='Date')
    day = fields.Char(string='Day')
    duration = fields.Float(string='Duration (HH:MM)')
    start_time = fields.Float(string='Start Time (24h format)')
    end_time = fields.Float(string='End Time (24h format)')

    def unlink(self):
        for rec in self:
            timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
                ['|', ('physician_id', '=', int(rec.schedule_id.doctor.id)), ('is_available', '=', True)])
            #print(timeslot)
            if timeslot:
                timeslot.sudo().unlink()
        return super(SmartMindDoctorScheduleLines, self).unlink()


class SmartMindDoctorScheduleTimeslot(models.Model):
    _name = "sm.shifa.physician.schedule.timeslot"
    _description = "Medical staffs Schedule Timeslot"
    _rec_name = 'available_time'

    physician_id = fields.Integer(string='Doctor')
    schedule_line_id = fields.Many2one('sm.shifa.physician.schedule.line', string='Schedule Lines', index=True,
                                       ondelete='cascade', help="Medical staffs Schedule Lines")
    medical_staff_id = fields.Many2one('oeh.medical.physician', related="schedule_line_id.schedule_id.doctor", readonly=False,
                                       store=True)
    date = fields.Date(string='Date')
    available_time = fields.Char(string='Time (HH:MM)', size=6)
    is_available = fields.Boolean(string='Available', default=lambda *a: 1) # True is available
