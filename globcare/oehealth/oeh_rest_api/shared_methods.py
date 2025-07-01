import uuid
from datetime import datetime, timedelta, time
from odoo.http import request
from odoo import http, _


class SmartMindSharedMethods:

    def _is_value_digit(self, value):
        try:
            number = int(value)
            return number
        except:
            return 0

    def _convert_to_time(self, str_time):
        hm = str_time.split(':')
        return int(hm[0]) + int(hm[1]) / 60

    def _get_tele_hvd_appointment_end(self, date):
        date_format = '%Y-%m-%d %H:%M:%S'
        input_date = date.strftime('%Y-%m-%d')
        schedule = request.env['oeh.medical.physician.line'].search([('date', '=', input_date)], limit=1)
        duration = False
        if schedule:
            duration = schedule.duration
        end_date = False
        if date and duration:
            end_date = datetime.strptime(str(date.strftime(date_format)), date_format) + timedelta(minutes=duration)
        else:
            return False
        return end_date

    def _create_jitsi_meeting(self, appointment_id):
        server_url = request.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        appointment = request.env['oeh.medical.appointment'].sudo().browse(int(appointment_id))
        # appointment = request.env['sm.telemedicine.appointment'].sudo().browse(int(appointment_id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link
        appointment.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })
        return meeting_link

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    def get_time_string(self, duration):
        result = ''
        currentHours = int(duration // 1)
        currentMinutes = int(round(duration % 1 * 60))
        if (currentHours <= 9):
            currentHours = "0" + str(currentHours)
        if (currentMinutes <= 9):
            currentMinutes = "0" + str(currentMinutes)
        result = str(currentHours) + ":" + str(currentMinutes)
        return result

    def get_image_url(self, image_type, model, model_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = base_url + '/web/image?' + 'model=' + model + '&id=' + str(model_id) + '&field=' + image_type
        return image_url

    def send_sms(self, model, inst_con, consultation):
        prescription_obj = request.env[model]
        domain = [('inst_con', '=', inst_con)]
        prescription = prescription_obj.search(domain)
        if consultation.patient.mobile:
            msg = "رقم وصفتك هي:%s" % (prescription.name)
            if consultation.pharmacy_chain:
                prs_msg = msg + " يمكنك صرفها من صيدلية %s ستجدها في ملفك الطبي " % (consultation.pharmacy_chain.name)
            else:
                prs_msg = msg + "  سيتم إرسال الوصفة الى تطبيقك خلال 10 دقائق و ستجدها في ملفك الطبي"

            consultation.send_sms(consultation.patient.mobile, prs_msg, model, prescription.id)
            return True
