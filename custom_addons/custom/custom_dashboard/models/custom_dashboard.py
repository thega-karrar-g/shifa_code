# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (C) 2022 - Present, Smart Mind (<https://smartmindsys.com/>). All Rights Reserved
#    Sehati, Globcare, Shifa, Hospital Management Solutions

import datetime
import calendar

from odoo import models, fields, api
from odoo.tools import date_utils
from odoo.http import request

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from datetime import date


class CustomDashboard(models.Model):
    _name = 'custom.dashboard'

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    oeh_dashboard_user_id = fields.Many2one("res.users", string="Oeh User", store=True)

    # Check Login User Group
    @api.model
    def login_user_group(self):
        login_user = self.env.user
        if login_user.has_group('oehealth.group_oeh_medical_manager'):
            return 1
        elif login_user.has_group('oehealth.group_oeh_medical_receptionist'):
            return 2
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_call_center'):
            return 3
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_head_doctor'):
            return 4
        elif login_user.has_group('oehealth.group_oeh_medical_physician'):
            return 5
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_telemedicine_doctor'):
            return 6
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_head_nurse'):
            return 7
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_head_physiotherapist'):
            return 8
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_hhc_nurse'):
            return 9
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_hhc_physiotherapist'):
            return 10
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_operation_manager'):
            return 11
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_lab_technician'):
            return 12
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_caregiver'):
            return 13
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_social_worker'):
            return 14
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_respiratory_therapist'):
            return 15
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_clinical_dietitian'):
            return 16
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_health_educator'):
            return 17
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_diabetic_educator'):
            return 18
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_home_visit_doctor'):
            return 19
        elif login_user.has_group('smartmind_shifa.group_oeh_medical_accountant'):
            return 20
        elif login_user.has_group('sm_caregiver.group_oeh_medical_super_caregiver'):
            return 21

    # ++++++++++ this method for more than one state  in urgent appointments (general)
    def get_count_data_appointment_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date_only as Date) = cast('{1}' as Date) and state in ({2})".format(
                    table, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date as Date) >= cast('{1}' as Date) AND cast(appointment_date_only as Date) <= cast('{2}' as Date) and state in ({3})".format(
                    table, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date_only as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state in ({3})".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select id from {0} where state in ({1})".format(table, state_val))

            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    # +++++++++ method for user urgent appointment (specific) more than one state ++++++++++++ #
    def get_user_urgent_data_appointment_count_filter(self, filter_type, table, doctor_column, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = {2}) and cast(t.appointment_date_only as Date) = cast('{3}' as Date) and t.state in ({4})"
                .format(table, doctor_column, self.env.uid, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                # "select id from {0} WHERE cast(appointment_date as Date) >= cast('{1}' as Date) AND cast(appointment_date as Date) <= cast('{2}' as Date) and state = '{3}'".format(
                #     table, start_day, end_day, state_val))
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date_only as Date) >= cast('{3}' as Date) AND cast(t.appointment_date as Date) <= cast('{4}' as Date) and t.state in ({5})".format(
                    table, doctor_column, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date_only as Date) between cast('{3}' as Date) and cast('{4}' as Date) and t.state in ({5})".format(
                    table, doctor_column, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and t.state in ({3})".format(
                    table, doctor_column, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_all_clinicians_urgent_data_appointment_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) = cast('{2}' as Date) and t.state in ({3}) "
                .format(table, self.env.uid, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) >= cast('{2}' as Date) AND cast(t.appointment_date as Date) <= cast('{3}' as Date) and t.state in ({4})".format(
                    table, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) between cast('{2}' as Date) and cast('{3}' as Date) and t.state in ({4})".format(
                    table, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and t.state in ({2})".format(
                    table, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_all_clinicians_data_appointment_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) = cast('{2}' as Date) and t.state = '{3}'"
                .format(table, self.env.uid, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) >= cast('{2}' as Date) AND cast(t.appointment_date as Date) <= cast('{3}' as Date) and t.state = '{4}'".format(
                    table, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and cast(t.appointment_date_only as Date) between cast('{2}' as Date) and cast('{3}' as Date) and t.state = '{4}'".format(
                    table, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select t.id from {0} t WHERE "
                "(t.nurse in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.doctor in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.physiotherapist in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.social_worker in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.diabetic_educator in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.clinical_dietitian in (select id from oeh_medical_physician where oeh_user_id = {1}) "
                "or t.respiratory_therapist in (select id from oeh_medical_physician where oeh_user_id = {1})) "
                "and t.state = '{2}'".format(
                    table, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    # +++++++++ method for one state for specific user +++++++++++++++ #
    def get_user_today_data_appointment_count_filter(self, filter_type, table, doctor_column, state_val):
        if filter_type == 'today':
            self._cr.execute(
                # "select id from {0} WHERE cast(appointment_date as Date) = cast('{1}' as Date) and state = '{2}'".format(
                #     table, date.today().strftime("%Y-%m-%d"), state_val))
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = {2}) and cast(t.appointment_date_only as Date) = cast('{3}' as Date) and t.state = '{4}'"
                .format(table, doctor_column, self.env.uid, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                # "select id from {0} WHERE cast(appointment_date as Date) >= cast('{1}' as Date) AND cast(appointment_date as Date) <= cast('{2}' as Date) and state = '{3}'".format(
                #     table, start_day, end_day, state_val))
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date_only as Date) >= cast('{3}' as Date) AND cast(t.appointment_date as Date) <= cast('{4}' as Date) and t.state = '{5}'".format(
                    table, doctor_column, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                # "select id from {0} WHERE cast(appointment_date as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state = '{3}'".format(
                #     table, curr_month_first_dt, curr_month_last_dt, state_val))
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date_only as Date) between cast('{3}' as Date) and cast('{4}' as Date) and t.state = '{5}'".format(
                    table, doctor_column, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                # "select id from {0} where state = '{1}'".format(table, state_val))
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and t.state = '{3}'".format(
                    table, doctor_column, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    # +++++++++++ method for one state to show all users appointments +++++++++ #
    def get_today_data_appointment_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date_only as Date) = cast('{1}' as Date) and state = '{2}'".format(
                    table, date.today().strftime("%Y-%m-%d"), state_val))
            # "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = {2}) and cast(t.appointment_date as Date) = cast('{3}' as Date) and t.state = '{4}'"
            #     .format(table, doctor_column, self.env.uid,date.today().strftime("%Y-%m-%d"),state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date_only as Date) >= cast('{1}' as Date) AND cast(appointment_date as Date) <= cast('{2}' as Date) and state = '{3}'".format(
                    table, start_day, end_day, state_val))
            # "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date as Date) >= cast('{3}' as Date) AND cast(t.appointment_date as Date) <= cast('{4}' as Date) and t.state = '{5}'".format(
            #     table, doctor_column, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select id from {0} WHERE cast(appointment_date_only as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state = '{3}'".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            # "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.appointment_date as Date) between cast('{3}' as Date) and cast('{4}' as Date) and t.state = '{5}'".format(
            #     table, doctor_column, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select id from {0} where state = '{1}'".format(table, state_val))
            # "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and t.state = '{3}'".format(
            #     table, doctor_column, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_data_appointment_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) = cast('{1}' as Date) and state in ({2})".format(
                    table, date.today().strftime("%Y-%m-%d"), state_val))

            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) >= cast('{1}' as Date) AND cast(create_date as Date) <= cast('{2}' as Date) and state in ({3})".format(
                    table, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state in ({3})".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute("select id from {0} where state in ({1})".format(table, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_data_multistate_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            # get ids of the today
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) = cast('{1}' as Date) and state in '{2}'".format(
                    table, date.today().strftime("%Y-%m-%d"), state_val))

            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) >= cast('{1}' as Date) AND cast(create_date as Date) <= cast('{2}' as Date) and state in '{3}'".format(
                    table, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state in '{3}'".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute("select id from {0} where state in ({1})".format(table, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_data_count_filter(self, filter_type, table, state_val):
        if filter_type == 'today':
            # get ids of the today
            # Check if the table has an 'active' field
            self._cr.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'active'
            """, (table,))

            # If the 'active' field exists, include it in the query
            if self._cr.fetchone():
                self._cr.execute("""
                    SELECT id 
                    FROM {0} 
                    WHERE cast(create_date AS DATE) = cast(%s AS DATE) 
                    AND active = TRUE 
                    AND state = %s
                """.format(table), (date.today().strftime("%Y-%m-%d"), state_val))
            else:
                # If the 'active' field does not exist, exclude the 'active=True' condition
                self._cr.execute("""
                    SELECT id 
                    FROM {0} 
                    WHERE cast(create_date AS DATE) = cast(%s AS DATE) 
                    AND state = %s
                """.format(table), (date.today().strftime("%Y-%m-%d"), state_val))


            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) >= cast('{1}' as Date) AND cast(create_date as Date) <= cast('{2}' as Date) and state = '{3}'".format(
                    table, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state = '{3}'".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute("select id from {0} where state = '{1}'".format(table, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_my_data_count_filter(self, filter_type, table, doctor_column, state_val):
        if filter_type == 'today':
            # get ids of the today
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.create_date as Date) = cast('{3}' as Date) and t.state = '{4}'".format(
                    table, doctor_column, self.env.uid, date.today().strftime("%Y-%m-%d"), state_val))

            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            # compute the week from today
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            # get ids of the week
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.create_date as Date) >= cast('{3}' as Date) AND cast(t.create_date as Date) <= cast('{4}' as Date) and t.state = '{5}'".format(
                    table, doctor_column, self.env.uid, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            # compute the month from today
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            # get ids of the month
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and cast(t.create_date as Date) between cast('{3}' as Date) and cast('{4}' as Date) and t.state = '{5}'".format(
                    table, doctor_column, self.env.uid, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            # get ids of the all data
            self._cr.execute(
                "select t.id from {0} t WHERE {1} in (select id from oeh_medical_physician where oeh_user_id = '{2}') and t.state = '{3}'".format(
                    table, doctor_column, self.env.uid, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_data_count_from_odoo_payment(self, state_val):
        query = """
                SELECT ap.id
                FROM account_payment ap
                JOIN account_move am ON ap.move_id = am.id
                WHERE am.state = %s
            """
        self._cr.execute(query, (state_val,))
        record = self._cr.fetchall()
        all_ids = [item for t in record for item in t]
        count = len(all_ids)
        all_ids.insert(0, count)
        return all_ids

    # Filter Today's Data
    @api.model
    def sm_data_today(self):
        filter_type = 'today'
        tele_app_ids = self.get_data_count_filter(filter_type, 'oeh_medical_appointment', 'Scheduled')
        missed_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'missed')
        cancel_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'canceled')
        tele_app_con_ids = self.get_data_count_filter('till_now', 'oeh_medical_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_tele_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'oeh_medical_appointment', states)
        hvd_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Scheduled')
        hvd_app_con_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_hvd_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hvd_appointment', states)
        physiotherapy_app_sc_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'scheduled')
        physiotherapy_app_co_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'head_physiotherapist')
        physiotherapy_app_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'operation_manager')
        physiotherapy_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment', 'team')
        physiotherapy_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                               'in_progress')
        physiotherapy_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'visit_done')
        physiotherapy_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'canceled')

        states = "'scheduled', 'head_physiotherapist', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_phy_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                                states)
        hhc_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'scheduled')
        hhc_app_hd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_doctor')
        hhc_app_hn_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_nurse')
        hhc_app_om_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'operation_manager')
        hhc_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'team')

        states = "'scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_hhc_sch_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hhc_appointment', states)
        tele_state = "'Scheduled', 'Confirmed', 'Start'"
        my_tele_today_ids = self.get_count_data_appointment_filter(filter_type, 'oeh_medical_appointment', tele_state)
        hvd_state = "'Scheduled', 'Confirmed', 'Start','Completed','canceled'"
        my_hvd_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hvd_appointment', hvd_state)
        hhc_state = "'scheduled','head_doctor','head_nurse','operation_manager','team','in_progress','visit_done','canceled'"
        my_hhc_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hhc_appointment', hhc_state)
        phy_state = "'scheduled','head_physiotherapist','operation_manager','team','in_progress','canceled','visit_done'"
        my_phy_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                  phy_state)
        pcr_state = "'scheduled','operation_manager','team','in_progress','canceled','visit_done'"
        my_pcr_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_pcr_appointment', pcr_state)
        pcr_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'scheduled')
        pcr_app_opm_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'operation_manager')
        pcr_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'team')
        states = "'scheduled', 'operation_manager', 'team'"
        my_pcr_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_pcr_appointment', states)
        service_request_ids = self.get_data_count_filter('till_now', 'sm_shifa_service_request', 'received')
        # service_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_service_request', 'received')
        noti_states = "'Start', 'Send'"
        notification_ids = self.get_data_multistate_count_filter('till_now', 'sm_physician_notification', noti_states)
        # notification_ids = self.get_data_count_filter(filter_type, 'sm_physician_notification', 'Send')
        image_states = "'Call Center', 'Team'"
        image_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_imaging_request', image_states)
        # image_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_imaging_request', 'Call Center')
        lab_states = "'Call Center', 'Team'"
        lab_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_lab_request', lab_states)
        # lab_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_lab_request', 'Call Center')
        investigation_states = "'Draft', 'Call Center', 'Team'"
        investigation_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_investigation',
                                                                  investigation_states)
        # investigation_ids = self.get_data_count_filter(filter_type, 'sm_shifa_investigation', 'Call Center')
        referral_states = "'start', 'call_center'"
        referral_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_referral', referral_states)
        # referral_ids = self.get_data_count_filter(filter_type, 'sm_shifa_referral', 'call_center')
        pay_states = "'Start', 'Send'"
        # requested_payments_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_requested_payments', pay_states)
        requested_payments_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Start')
        requested_payments_send_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Send')
        requested_payments_paid_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Paid')
        cancel_states = "'received', 'operation_manager', 'Processed'"
        # cancellation_refund_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_cancellation_refund', cancel_states)
        cancellation_refund_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'received')
        cancellation_refund_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund',
                                                                'operation_manager')
        cancellation_refund_pr_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'Processed')

        hhc_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type, 'sm_shifa_hhc_appointment',
                                                                              'team')
        tele_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type, 'oeh_medical_appointment',
                                                                               'Confirmed')
        hhc_tod_tm_soc_wor_ids = self.get_all_clinicians_data_appointment_count_filter('till_now',
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_soc_wor_ids = self.get_today_data_appointment_count_filter(filter_type,
                                                                                'oeh_medical_appointment', 'Confirmed')
        hhc_tod_tm_hhc_nurse_ids = self.get_all_clinicians_data_appointment_count_filter('till_now',
                                                                                         'sm_shifa_hhc_appointment',
                                                                                         'team')
        tele_tod_con_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor',
                                                                                       'Confirmed')
        pcr_tod_tm_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_pcr_appointment',
                                                                                     't.nurse', 'team')
        pcr_tod_tm_lab_technician_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_pcr_appointment',
                                                                                          't.lab_technician', 'team')
        phy_tod_tm_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_physiotherapy_appointment',
                                                                                   't.physiotherapist', 'team')
        hhc_tod_tm_hhc_phy_ids = self.get_all_clinicians_data_appointment_count_filter('till_now',
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        tele_tod_con_tele_app_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                      'oeh_medical_appointment',
                                                                                      't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_doctor_ids = self.get_all_clinicians_data_appointment_count_filter('till_now',
                                                                                          'sm_shifa_hhc_appointment',
                                                                                          'team')
        tele_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                        'oeh_medical_appointment',
                                                                                        't.doctor', 'Confirmed')
        hvd_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hvd_appointment',
                                                                                       't.doctor', 'Confirmed')
        tele_tod_con_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor', tele_state)
        hhc_tod_tm_head_phy_ids = self.get_all_clinicians_urgent_data_appointment_count_filter('till_now',
                                                                                               'sm_shifa_hhc_appointment',
                                                                                               hhc_state)
        phy_tod_tm_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_physiotherapy_appointment',
                                                                                     't.physiotherapist', phy_state)
        hhc_tod_tm_head_nurse_ids = self.get_all_clinicians_urgent_data_appointment_count_filter('till_now',
                                                                                                 'sm_shifa_hhc_appointment',
                                                                                                 hhc_state)
        pcr_tod_tm_head_nurse_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_pcr_appointment',
                                                                                       't.nurse', pcr_state)
        hvd_tod_con_head_doctor_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hvd_appointment',
                                                                                         't.doctor', hvd_state)
        hhc_tod_tm_head_doctor_ids = self.get_all_clinicians_urgent_data_appointment_count_filter('till_now',
                                                                                                  'sm_shifa_hhc_appointment',
                                                                                                  hhc_state)

        my_physiotherapy_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'team')
        my_physiotherapy_app_sch_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                     't.physiotherapist', 'scheduled')
        my_physiotherapy_app_hp_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'head_physiotherapist')
        my_physiotherapy_app_op_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'operation_manager')
        my_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.nurse', 'team')
        my_hhc_app_phy_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment',
                                                              't.physiotherapist', 'team')
        my_h_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                            'team')

        my_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                            'Confirmed')
        my_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                           'Confirmed')

        my_tele_app_hn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_tele_app_hdphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                  'Confirmed')
        my_tele_app_hhcn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                 'Confirmed')
        my_hhcn_pcr_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 't.nurse',
                                                               'team')
        my_tele_app_hhcphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                   'Confirmed')
        my_rh_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                             'team')
        my_rh_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_rh_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                              'Confirmed')
        call_center_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'call_center')
        call_center_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'operation_manager')
        hhc_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'visit_done')
        hhc_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'in_progress')
        hhc_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'canceled')
        web_req_ids = self.get_data_count_filter('till_now', 'sm_shifa_web_request', 'Received')

        # Sleep Medicine Request
        slep_me_req_unpaid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'unpaid')
        slep_me_req_paid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'paid')
        slep_me_req_ev_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'evaluation')
        slep_me_req_sch_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'scheduling')
        # Caregiver Contract
        car_cont_unpaid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'unpaid')
        car_cont_paid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'paid')
        car_cont_ev_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'evaluation')
        car_cont_as_car_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'assign_caregiver')
        car_cont_act_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'active')
        car_cont_hrq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'holdreq')
        car_cont_trq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'terminationreq')
        car_cont_rew_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'renew')
        car_cont_hol_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'hold')
        car_cont_rea_req_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'reactivation_request')

        hhc_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'requestCancellation')
        phy_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                    'requestCancellation')

        draft_payment_ids = self.get_data_count_from_odoo_payment('draft')

        data = {
            'tele_app_ids': tele_app_ids,
            'missed_medicines_ids': missed_medicines_ids,
            'cancel_medicines_ids': cancel_medicines_ids,
            'tele_app_con_ids': tele_app_con_ids,
            'my_tele_sch_con_ids': my_tele_sch_con_ids,
            'hvd_app_sch_ids': hvd_app_sch_ids,
            'hvd_app_con_ids': hvd_app_con_ids,
            'my_hvd_sch_con_ids': my_hvd_sch_con_ids,
            'physiotherapy_app_sc_ids': physiotherapy_app_sc_ids,
            'physiotherapy_app_co_ids': physiotherapy_app_co_ids,
            'physiotherapy_app_op_ids': physiotherapy_app_op_ids,
            'physiotherapy_app_tm_ids': physiotherapy_app_tm_ids,
            'physiotherapy_app_inp_ids': physiotherapy_app_inp_ids,
            'physiotherapy_app_vd_ids': physiotherapy_app_vd_ids,
            'physiotherapy_app_ca_ids': physiotherapy_app_ca_ids,
            'my_phy_all_ids': my_phy_all_ids,
            'hhc_app_sch_ids': hhc_app_sch_ids,
            'hhc_app_hd_ids': hhc_app_hd_ids,
            'hhc_app_hn_ids': hhc_app_hn_ids,
            'hhc_app_om_ids': hhc_app_om_ids,
            'hhc_app_tm_ids': hhc_app_tm_ids,
            'my_hhc_sch_all_ids': my_hhc_sch_all_ids,
            'my_tele_today_ids': my_tele_today_ids,
            'my_hvd_today_ids': my_hvd_today_ids,
            'my_hhc_today_ids': my_hhc_today_ids,
            'my_phy_today_ids': my_phy_today_ids,
            'my_pcr_today_ids': my_pcr_today_ids,
            'pcr_app_sch_ids': pcr_app_sch_ids,
            'pcr_app_opm_ids': pcr_app_opm_ids,
            'pcr_app_tm_ids': pcr_app_tm_ids,
            'my_pcr_all_ids': my_pcr_all_ids,
            'service_request_ids': service_request_ids,
            'notification_ids': notification_ids,
            'image_request_ids': image_request_ids,
            'lab_request_ids': lab_request_ids,
            'investigation_ids': investigation_ids,
            'referral_ids': referral_ids,
            'requested_payments_ids': requested_payments_ids,
            'requested_payments_send_ids': requested_payments_send_ids,
            'requested_payments_paid_ids': requested_payments_paid_ids,
            'cancellation_refund_ids': cancellation_refund_ids,
            'cancellation_refund_pr_ids': cancellation_refund_pr_ids,
            'cancellation_refund_op_ids': cancellation_refund_op_ids,
            'hhc_tod_tm_res_the_ids': hhc_tod_tm_res_the_ids,
            'tele_tod_tm_res_the_ids': tele_tod_tm_res_the_ids,
            'hhc_tod_tm_soc_wor_ids': hhc_tod_tm_soc_wor_ids,
            'tele_tod_con_soc_wor_ids': tele_tod_con_soc_wor_ids,
            'hhc_tod_tm_hhc_nurse_ids': hhc_tod_tm_hhc_nurse_ids,
            'tele_tod_con_hhc_nurse_ids': tele_tod_con_hhc_nurse_ids,
            'pcr_tod_tm_hhc_nurse_ids': pcr_tod_tm_hhc_nurse_ids,
            'pcr_tod_tm_lab_technician_ids': pcr_tod_tm_lab_technician_ids,
            'phy_tod_tm_hhc_phy_ids': phy_tod_tm_hhc_phy_ids,
            'hhc_tod_tm_hhc_phy_ids': hhc_tod_tm_hhc_phy_ids,
            'tele_tod_con_hhc_phy_ids': tele_tod_con_hhc_phy_ids,
            'tele_tod_con_tele_app_ids': tele_tod_con_tele_app_ids,
            'hhc_tod_tm_hhc_doctor_ids': hhc_tod_tm_hhc_doctor_ids,
            'tele_tod_con_hhc_doctor_ids': tele_tod_con_hhc_doctor_ids,
            'hvd_tod_con_hhc_doctor_ids': hvd_tod_con_hhc_doctor_ids,
            'tele_tod_con_head_phy_ids': tele_tod_con_head_phy_ids,
            'hhc_tod_tm_head_phy_ids': hhc_tod_tm_head_phy_ids,
            'phy_tod_tm_head_phy_ids': phy_tod_tm_head_phy_ids,
            'hhc_tod_tm_head_nurse_ids': hhc_tod_tm_head_nurse_ids,
            'pcr_tod_tm_head_nurse_ids': pcr_tod_tm_head_nurse_ids,
            'hvd_tod_con_head_doctor_ids': hvd_tod_con_head_doctor_ids,
            'hhc_tod_tm_head_doctor_ids': hhc_tod_tm_head_doctor_ids,
            'call_center_ids': call_center_ids,
            'call_center_op_ids': call_center_op_ids,
            'hhc_app_vd_ids': hhc_app_vd_ids,
            'hhc_app_inp_ids': hhc_app_inp_ids,
            'hhc_app_ca_ids': hhc_app_ca_ids,
            'web_req_ids': web_req_ids,

            'my_hhc_app_tm_ids': my_hhc_app_tm_ids,
            'my_hhc_app_phy_tm_ids': my_hhc_app_phy_tm_ids,
            'my_physiotherapy_app_tm_ids': my_physiotherapy_app_tm_ids,
            'my_physiotherapy_app_sch_ids': my_physiotherapy_app_sch_ids,
            'my_physiotherapy_app_hp_ids': my_physiotherapy_app_hp_ids,
            'my_physiotherapy_app_op_ids': my_physiotherapy_app_op_ids,
            'my_h_hhc_app_tm_ids': my_h_hhc_app_tm_ids,
            'my_tele_app_con_ids': my_tele_app_con_ids,
            'my_hvd_app_con_ids': my_hvd_app_con_ids,
            'my_tele_app_hn_con_ids': my_tele_app_hn_con_ids,
            'my_tele_app_hdphy_con_ids': my_tele_app_hdphy_con_ids,
            'my_tele_app_hhcn_con_ids': my_tele_app_hhcn_con_ids,
            'my_hhcn_pcr_app_tm_ids': my_hhcn_pcr_app_tm_ids,
            'my_tele_app_hhcphy_con_ids': my_tele_app_hhcphy_con_ids,
            'my_rh_hhc_app_tm_ids': my_rh_hhc_app_tm_ids,
            'my_rh_tele_app_con_ids': my_rh_tele_app_con_ids,
            'my_rh_hvd_app_con_ids': my_rh_hvd_app_con_ids,

            # Sleep Medicine Request
            'slep_me_req_unpaid_ids': slep_me_req_unpaid_ids,
            'slep_me_req_paid_ids': slep_me_req_paid_ids,
            'slep_me_req_ev_ids': slep_me_req_ev_ids,
            'slep_me_req_sch_ids': slep_me_req_sch_ids,
            # Caregiver Contract
            'car_cont_unpaid_ids': car_cont_unpaid_ids,
            'car_cont_paid_ids': car_cont_paid_ids,
            'car_cont_ev_ids': car_cont_ev_ids,
            'car_cont_as_car_ids': car_cont_as_car_ids,
            'car_cont_act_ids': car_cont_act_ids,
            'car_cont_hrq_ids': car_cont_hrq_ids,
            'car_cont_trq_ids': car_cont_trq_ids,
            'car_cont_rew_ids': car_cont_rew_ids,
            'car_cont_hol_ids': car_cont_hol_ids,
            'car_cont_rea_req_ids': car_cont_rea_req_ids,

            'hhc_app_cr_ids': hhc_app_cr_ids,
            'phy_app_cr_ids': phy_app_cr_ids,
            'draft_payment_ids': draft_payment_ids,
        }
        return data

    # Filter This Week Data
    @api.model
    def sm_data_week(self):
        filter_type = 'week'
        tele_app_ids = self.get_data_count_filter(filter_type, 'oeh_medical_appointment', 'Scheduled')
        missed_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'missed')
        cancel_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'canceled')
        tele_app_con_ids = self.get_data_count_filter('till_now', 'oeh_medical_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_tele_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'oeh_medical_appointment', states)
        hvd_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Scheduled')
        hvd_app_con_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_hvd_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hvd_appointment', states)
        physiotherapy_app_sc_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'scheduled')
        physiotherapy_app_co_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'head_physiotherapist')
        physiotherapy_app_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'operation_manager')
        physiotherapy_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment', 'team')
        physiotherapy_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                               'in_progress')
        physiotherapy_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'visit_done')
        physiotherapy_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'canceled')
        states = "'scheduled', 'head_physiotherapist', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_phy_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                                states)
        hhc_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'scheduled')
        hhc_app_hd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_doctor')
        hhc_app_hn_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_nurse')
        hhc_app_om_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'operation_manager')
        hhc_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'team')
        states = "'scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_hhc_sch_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hhc_appointment', states)
        tele_state = "'Scheduled', 'Confirmed', 'Start'"
        my_tele_today_ids = self.get_count_data_appointment_filter(filter_type, 'oeh_medical_appointment', tele_state)
        hvd_state = "'Scheduled', 'Confirmed', 'Start'"
        my_hvd_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hvd_appointment', hvd_state)
        hhc_state = "'scheduled','head_doctor','head_nurse','operation_manager','team','in_progress','visit_done','canceled'"
        my_hhc_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hhc_appointment', hhc_state)
        phy_state = "'scheduled','head_physiotherapist','operation_manager','team','in_progress','canceled','visit_done'"
        my_phy_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                  phy_state)
        pcr_state = "'scheduled','operation_manager','team','in_progress','canceled','visit_done'"
        my_pcr_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_pcr_appointment', pcr_state)
        pcr_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'scheduled')
        pcr_app_opm_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'operation_manager')
        pcr_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_pcr_appointment', 'team')
        states = "'scheduled', 'operation_manager', 'team'"
        my_pcr_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_pcr_appointment', states)
        service_request_ids = self.get_data_count_filter('till_now', 'sm_shifa_service_request', 'received')
        # service_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_service_request', 'received')
        noti_states = "'Start', 'Send'"
        notification_ids = self.get_data_multistate_count_filter('till_now', 'sm_physician_notification', noti_states)
        # notification_ids = self.get_data_count_filter(filter_type, 'sm_physician_notification', 'Send')
        image_states = "'Call Center', 'Team'"
        image_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_imaging_request', image_states)
        # image_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_imaging_request', 'Call Center')
        lab_states = "'Call Center', 'Team'"
        lab_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_lab_request', lab_states)
        # lab_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_lab_request', 'Call Center')
        investigation_states = "'Draft', 'Call Center', 'Team'"
        investigation_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_investigation',
                                                                  investigation_states)
        # investigation_ids = self.get_data_count_filter(filter_type, 'sm_shifa_investigation', 'Call Center')
        referral_states = "'start', 'call_center'"
        referral_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_referral', referral_states)
        # referral_ids = self.get_data_count_filter(filter_type, 'sm_shifa_referral', 'call_center')
        pay_states = "'Start', 'Send'"
        # requested_payments_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_requested_payments', pay_states)
        requested_payments_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Start')
        requested_payments_send_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Send')
        requested_payments_paid_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Paid')
        cancel_states = "'received', 'operation_manager', 'Processed'"
        # cancellation_refund_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_cancellation_refund', cancel_states)
        cancellation_refund_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'received')
        cancellation_refund_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund',
                                                                'operation_manager')
        cancellation_refund_pr_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund',
                                                                'Processed')
        hhc_tod_tm_res_the_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type, 'oeh_medical_appointment',
                                                                               'Confirmed')
        hhc_tod_tm_soc_wor_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_soc_wor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_nurse_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hhc_appointment',
                                                                                         'team')
        tele_tod_con_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor',
                                                                                       'Confirmed')
        pcr_tod_tm_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_pcr_appointment',
                                                                                     't.nurse', 'team')
        pcr_tod_tm_lab_technician_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_pcr_appointment',
                                                                                          't.lab_technician', 'team')
        phy_tod_tm_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_physiotherapy_appointment',
                                                                                   't.physiotherapist', 'team')
        hhc_tod_tm_hhc_phy_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        tele_tod_con_tele_app_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                      'oeh_medical_appointment',
                                                                                      't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_doctor_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_hhc_appointment',
                                                                                          'team')
        tele_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                        'oeh_medical_appointment',
                                                                                        't.doctor', 'Confirmed')
        hvd_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hvd_appointment',
                                                                                       't.doctor', 'Confirmed')
        tele_tod_con_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor', tele_state)
        hhc_tod_tm_head_phy_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                               'sm_shifa_hhc_appointment',
                                                                                               hhc_state)
        phy_tod_tm_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_physiotherapy_appointment',
                                                                                     't.physiotherapist', phy_state)
        hhc_tod_tm_head_nurse_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                                 'sm_shifa_hhc_appointment',
                                                                                                 hhc_state)
        pcr_tod_tm_head_nurse_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_pcr_appointment',
                                                                                       't.nurse', pcr_state)
        hvd_tod_con_head_doctor_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hvd_appointment',
                                                                                         't.doctor', hvd_state)
        hhc_tod_tm_head_doctor_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                                  'sm_shifa_hhc_appointment',
                                                                                                  hhc_state)

        my_physiotherapy_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'team')
        my_physiotherapy_app_sch_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                     't.physiotherapist', 'scheduled')
        my_physiotherapy_app_hp_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'head_physiotherapist')
        my_physiotherapy_app_op_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'operation_manager')
        my_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.nurse', 'team')
        my_hhc_app_phy_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment',
                                                              't.physiotherapist', 'team')
        my_h_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                            'team')
        my_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                            'Confirmed')
        my_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                           'Confirmed')
        my_tele_app_hn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_tele_app_hdphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                  'Confirmed')
        my_tele_app_hhcn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                 'Confirmed')
        my_hhcn_pcr_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 't.nurse',
                                                               'team')
        my_tele_app_hhcphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                   'Confirmed')
        my_rh_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                             'team')
        my_rh_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_rh_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                              'Confirmed')
        call_center_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'call_center')
        call_center_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'operation_manager')
        hhc_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'visit_done')
        hhc_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'in_progress')
        hhc_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'canceled')
        web_req_ids = self.get_data_count_filter('till_now', 'sm_shifa_web_request', 'Received')

        # Sleep Medicine Request
        slep_me_req_unpaid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'unpaid')
        slep_me_req_paid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'paid')
        slep_me_req_ev_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'evaluation')
        slep_me_req_sch_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'scheduling')
        # Caregiver Contract
        car_cont_unpaid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'unpaid')
        car_cont_paid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'paid')
        car_cont_ev_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'evaluation')
        car_cont_as_car_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'assign_caregiver')
        car_cont_act_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'active')
        car_cont_hrq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'holdreq')
        car_cont_trq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'terminationreq')
        car_cont_rew_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'renew')
        car_cont_hol_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'hold')
        car_cont_rea_req_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'reactivation_request')

        hhc_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'requestCancellation')
        phy_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                    'requestCancellation')

        draft_payment_ids = self.get_data_count_from_odoo_payment('draft')

        data = {
            'tele_app_ids': tele_app_ids,
            'missed_medicines_ids': missed_medicines_ids,
            'cancel_medicines_ids': cancel_medicines_ids,
            'tele_app_con_ids': tele_app_con_ids,
            'my_tele_sch_con_ids': my_tele_sch_con_ids,
            'hvd_app_sch_ids': hvd_app_sch_ids,
            'hvd_app_con_ids': hvd_app_con_ids,
            'my_hvd_sch_con_ids': my_hvd_sch_con_ids,
            'physiotherapy_app_sc_ids': physiotherapy_app_sc_ids,
            'physiotherapy_app_co_ids': physiotherapy_app_co_ids,
            'physiotherapy_app_op_ids': physiotherapy_app_op_ids,
            'physiotherapy_app_tm_ids': physiotherapy_app_tm_ids,
            'physiotherapy_app_inp_ids': physiotherapy_app_inp_ids,
            'physiotherapy_app_vd_ids': physiotherapy_app_vd_ids,
            'physiotherapy_app_ca_ids': physiotherapy_app_ca_ids,
            'my_phy_all_ids': my_phy_all_ids,
            'hhc_app_sch_ids': hhc_app_sch_ids,
            'hhc_app_hd_ids': hhc_app_hd_ids,
            'hhc_app_hn_ids': hhc_app_hn_ids,
            'hhc_app_om_ids': hhc_app_om_ids,
            'hhc_app_tm_ids': hhc_app_tm_ids,
            'my_hhc_sch_all_ids': my_hhc_sch_all_ids,
            'my_tele_today_ids': my_tele_today_ids,
            'my_hvd_today_ids': my_hvd_today_ids,
            'my_hhc_today_ids': my_hhc_today_ids,
            'my_phy_today_ids': my_phy_today_ids,
            'my_pcr_today_ids': my_pcr_today_ids,
            'pcr_app_sch_ids': pcr_app_sch_ids,
            'pcr_app_opm_ids': pcr_app_opm_ids,
            'pcr_app_tm_ids': pcr_app_tm_ids,
            'my_pcr_all_ids': my_pcr_all_ids,
            'service_request_ids': service_request_ids,
            'notification_ids': notification_ids,
            'image_request_ids': image_request_ids,
            'lab_request_ids': lab_request_ids,
            'investigation_ids': investigation_ids,
            'referral_ids': referral_ids,
            'requested_payments_ids': requested_payments_ids,
            'requested_payments_send_ids': requested_payments_send_ids,
            'requested_payments_paid_ids': requested_payments_paid_ids,
            'cancellation_refund_ids': cancellation_refund_ids,
            'cancellation_refund_pr_ids': cancellation_refund_pr_ids,
            'cancellation_refund_op_ids': cancellation_refund_op_ids,
            'hhc_tod_tm_res_the_ids': hhc_tod_tm_res_the_ids,
            'tele_tod_tm_res_the_ids': tele_tod_tm_res_the_ids,
            'hhc_tod_tm_soc_wor_ids': hhc_tod_tm_soc_wor_ids,
            'tele_tod_con_soc_wor_ids': tele_tod_con_soc_wor_ids,
            'hhc_tod_tm_hhc_nurse_ids': hhc_tod_tm_hhc_nurse_ids,
            'tele_tod_con_hhc_nurse_ids': tele_tod_con_hhc_nurse_ids,
            'pcr_tod_tm_hhc_nurse_ids': pcr_tod_tm_hhc_nurse_ids,
            'pcr_tod_tm_lab_technician_ids': pcr_tod_tm_lab_technician_ids,
            'phy_tod_tm_hhc_phy_ids': phy_tod_tm_hhc_phy_ids,
            'hhc_tod_tm_hhc_phy_ids': hhc_tod_tm_hhc_phy_ids,
            'tele_tod_con_hhc_phy_ids': tele_tod_con_hhc_phy_ids,
            'tele_tod_con_tele_app_ids': tele_tod_con_tele_app_ids,
            'hhc_tod_tm_hhc_doctor_ids': hhc_tod_tm_hhc_doctor_ids,
            'tele_tod_con_hhc_doctor_ids': tele_tod_con_hhc_doctor_ids,
            'hvd_tod_con_hhc_doctor_ids': hvd_tod_con_hhc_doctor_ids,
            'tele_tod_con_head_phy_ids': tele_tod_con_head_phy_ids,
            'hhc_tod_tm_head_phy_ids': hhc_tod_tm_head_phy_ids,
            'phy_tod_tm_head_phy_ids': phy_tod_tm_head_phy_ids,
            'hhc_tod_tm_head_nurse_ids': hhc_tod_tm_head_nurse_ids,
            'pcr_tod_tm_head_nurse_ids': pcr_tod_tm_head_nurse_ids,
            'hvd_tod_con_head_doctor_ids': hvd_tod_con_head_doctor_ids,
            'hhc_tod_tm_head_doctor_ids': hhc_tod_tm_head_doctor_ids,
            'call_center_ids': call_center_ids,
            'call_center_op_ids': call_center_op_ids,
            'hhc_app_vd_ids': hhc_app_vd_ids,
            'hhc_app_inp_ids': hhc_app_inp_ids,
            'hhc_app_ca_ids': hhc_app_ca_ids,
            'web_req_ids': web_req_ids,

            'my_hhc_app_tm_ids': my_hhc_app_tm_ids,
            'my_hhc_app_phy_tm_ids': my_hhc_app_phy_tm_ids,
            'my_physiotherapy_app_tm_ids': my_physiotherapy_app_tm_ids,
            'my_physiotherapy_app_sch_ids': my_physiotherapy_app_sch_ids,
            'my_physiotherapy_app_hp_ids': my_physiotherapy_app_hp_ids,
            'my_physiotherapy_app_op_ids': my_physiotherapy_app_op_ids,
            'my_h_hhc_app_tm_ids': my_h_hhc_app_tm_ids,
            'my_tele_app_con_ids': my_tele_app_con_ids,
            'my_tele_app_hn_con_ids': my_tele_app_hn_con_ids,
            'my_tele_app_hdphy_con_ids': my_tele_app_hdphy_con_ids,
            'my_tele_app_hhcn_con_ids': my_tele_app_hhcn_con_ids,
            'my_hhcn_pcr_app_tm_ids': my_hhcn_pcr_app_tm_ids,
            'my_tele_app_hhcphy_con_ids': my_tele_app_hhcphy_con_ids,
            'my_hvd_app_con_ids': my_hvd_app_con_ids,
            'my_rh_hhc_app_tm_ids': my_rh_hhc_app_tm_ids,
            'my_rh_tele_app_con_ids': my_rh_tele_app_con_ids,
            'my_rh_hvd_app_con_ids': my_rh_hvd_app_con_ids,

            # Sleep Medicine Request
            'slep_me_req_unpaid_ids': slep_me_req_unpaid_ids,
            'slep_me_req_paid_ids': slep_me_req_paid_ids,
            'slep_me_req_ev_ids': slep_me_req_ev_ids,
            'slep_me_req_sch_ids': slep_me_req_sch_ids,
            # Caregiver Contract
            'car_cont_unpaid_ids': car_cont_unpaid_ids,
            'car_cont_paid_ids': car_cont_paid_ids,
            'car_cont_ev_ids': car_cont_ev_ids,
            'car_cont_as_car_ids': car_cont_as_car_ids,
            'car_cont_act_ids': car_cont_act_ids,
            'car_cont_hrq_ids': car_cont_hrq_ids,
            'car_cont_trq_ids': car_cont_trq_ids,
            'car_cont_rew_ids': car_cont_rew_ids,
            'car_cont_hol_ids': car_cont_hol_ids,
            'car_cont_rea_req_ids': car_cont_rea_req_ids,

            'hhc_app_cr_ids': hhc_app_cr_ids,
            'phy_app_cr_ids': phy_app_cr_ids,
            'draft_payment_ids': draft_payment_ids,
        }
        return data

    # Filter This Month Data
    @api.model
    def sm_data_month(self):
        filter_type = 'month'
        tele_app_ids = self.get_data_count_filter(filter_type, 'oeh_medical_appointment', 'Scheduled')
        missed_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'missed')
        cancel_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'canceled')
        tele_app_con_ids = self.get_data_count_filter('till_now', 'oeh_medical_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_tele_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'oeh_medical_appointment', states)
        hvd_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Scheduled')
        hvd_app_con_ids = self.get_data_count_filter('till_now', 'sm_shifa_hvd_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_hvd_sch_con_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hvd_appointment', states)
        physiotherapy_app_sc_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'scheduled')
        physiotherapy_app_co_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'head_physiotherapist')
        physiotherapy_app_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'operation_manager')
        physiotherapy_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment', 'team')
        physiotherapy_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                               'in_progress')
        physiotherapy_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'visit_done')
        physiotherapy_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                              'canceled')
        states = "'scheduled', 'head_physiotherapist', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_phy_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_physiotherapy_appointment',
                                                                states)
        hhc_app_sch_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'scheduled')
        hhc_app_hd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_doctor')
        hhc_app_hn_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'head_nurse')
        hhc_app_om_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'operation_manager')
        hhc_app_tm_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'team')
        states = "'scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_hhc_sch_all_ids = self.get_data_appointment_count_filter('till_now', 'sm_shifa_hhc_appointment', states)
        tele_state = "'Scheduled', 'Confirmed', 'Start'"
        my_tele_today_ids = self.get_count_data_appointment_filter(filter_type, 'oeh_medical_appointment', tele_state)
        hvd_state = "'Scheduled', 'Confirmed', 'Start'"
        my_hvd_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hvd_appointment', hvd_state)
        hhc_state = "'scheduled','head_doctor','head_nurse','operation_manager','team','in_progress','visit_done','canceled'"
        my_hhc_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hhc_appointment', hhc_state)
        phy_state = "'scheduled','head_physiotherapist','operation_manager','team','in_progress','canceled','visit_done'"
        my_phy_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                  phy_state)
        pcr_state = "'scheduled','operation_manager','team','in_progress','canceled','visit_done'"
        my_pcr_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_pcr_appointment', pcr_state)
        pcr_app_sch_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'scheduled')
        pcr_app_opm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'operation_manager')
        pcr_app_tm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'team')
        states = "'scheduled', 'operation_manager', 'team'"
        my_pcr_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_pcr_appointment', states)
        service_request_ids = self.get_data_count_filter('till_now', 'sm_shifa_service_request', 'received')
        # service_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_service_request', 'received')
        noti_states = "'Start', 'Send'"
        notification_ids = self.get_data_multistate_count_filter('till_now', 'sm_physician_notification', noti_states)
        # notification_ids = self.get_data_count_filter(filter_type, 'sm_physician_notification', 'Send')
        image_states = "'Call Center', 'Team'"
        image_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_imaging_request', image_states)
        # image_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_imaging_request', 'Call Center')
        lab_states = "'Call Center', 'Team'"
        lab_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_lab_request', lab_states)
        # lab_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_lab_request', 'Call Center')
        investigation_states = "'Draft', 'Call Center', 'Team'"
        investigation_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_investigation',
                                                                  investigation_states)
        # investigation_ids = self.get_data_count_filter(filter_type, 'sm_shifa_investigation', 'Call Center')
        referral_states = "'start', 'call_center'"
        referral_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_referral', referral_states)
        # referral_ids = self.get_data_count_filter(filter_type, 'sm_shifa_referral', 'call_center')
        pay_states = "'Start', 'Send'"
        # requested_payments_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_requested_payments', pay_states)
        requested_payments_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Start')
        requested_payments_send_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Send')
        requested_payments_paid_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Paid')
        cancel_states = "'received', 'operation_manager', 'Processed'"
        # cancellation_refund_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_cancellation_refund', cancel_states)
        cancellation_refund_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'received')
        cancellation_refund_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund',
                                                                'operation_manager')
        cancellation_refund_pr_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'Processed')
        hhc_tod_tm_res_the_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type, 'oeh_medical_appointment',
                                                                               'Confirmed')
        hhc_tod_tm_soc_wor_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_soc_wor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_nurse_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hhc_appointment',
                                                                                         'team')
        tele_tod_con_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor',
                                                                                       'Confirmed')
        pcr_tod_tm_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_pcr_appointment',
                                                                                     't.nurse', 'team')
        pcr_tod_tm_lab_technician_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_pcr_appointment',
                                                                                          't.lab_technician', 'team')
        phy_tod_tm_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_physiotherapy_appointment',
                                                                                   't.physiotherapist', 'team')
        hhc_tod_tm_hhc_phy_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hhc_appointment',
                                                                                       'team')
        tele_tod_con_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        tele_tod_con_tele_app_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                      'oeh_medical_appointment',
                                                                                      't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_doctor_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_hhc_appointment',
                                                                                          'team')
        tele_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                        'oeh_medical_appointment',
                                                                                        't.doctor', 'Confirmed')
        hvd_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hvd_appointment',
                                                                                       't.doctor', 'Confirmed')
        tele_tod_con_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor', tele_state)
        hhc_tod_tm_head_phy_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                               'sm_shifa_hhc_appointment',
                                                                                               hhc_state)
        phy_tod_tm_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_physiotherapy_appointment',
                                                                                     't.physiotherapist', phy_state)
        hhc_tod_tm_head_nurse_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                                 'sm_shifa_hhc_appointment',
                                                                                                 hhc_state)
        pcr_tod_tm_head_nurse_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_pcr_appointment',
                                                                                       't.nurse', pcr_state)
        hvd_tod_con_head_doctor_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hvd_appointment',
                                                                                         't.doctor', hvd_state)
        hhc_tod_tm_head_doctor_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                                  'sm_shifa_hhc_appointment',
                                                                                                  hhc_state)

        my_physiotherapy_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'team')
        my_physiotherapy_app_sch_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                     't.physiotherapist', 'scheduled')
        my_physiotherapy_app_hp_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'head_physiotherapist')
        my_physiotherapy_app_op_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'operation_manager')
        my_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.nurse', 'team')
        my_hhc_app_phy_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment',
                                                              't.physiotherapist', 'team')
        my_h_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                            'team')
        my_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                            'Confirmed')
        my_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                           'Confirmed')
        my_tele_app_hn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_tele_app_hdphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                  'Confirmed')
        my_tele_app_hhcn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                 'Confirmed')
        my_hhcn_pcr_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 't.nurse',
                                                               'team')
        my_tele_app_hhcphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                   'Confirmed')
        my_rh_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                             'team')
        my_rh_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_rh_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                              'Confirmed')
        call_center_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'call_center')
        call_center_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'operation_manager')
        hhc_app_vd_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'visit_done')
        hhc_app_inp_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'in_progress')
        hhc_app_ca_ids = self.get_data_count_filter('till_now', 'sm_shifa_hhc_appointment', 'canceled')
        web_req_ids = self.get_data_count_filter('till_now', 'sm_shifa_web_request', 'Received')

        # Sleep Medicine Request
        slep_me_req_unpaid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'unpaid')
        slep_me_req_paid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'paid')
        slep_me_req_ev_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'evaluation')
        slep_me_req_sch_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'scheduling')
        # Caregiver Contract
        car_cont_unpaid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'unpaid')
        car_cont_paid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'paid')
        car_cont_ev_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'evaluation')
        car_cont_as_car_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'assign_caregiver')
        car_cont_act_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'active')
        car_cont_hrq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'holdreq')
        car_cont_trq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'terminationreq')
        car_cont_rew_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'renew')
        car_cont_hol_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'hold')
        car_cont_rea_req_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'reactivation_request')

        hhc_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'requestCancellation')
        phy_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                    'requestCancellation')

        draft_payment_ids = self.get_data_count_from_odoo_payment('draft')

        data = {
            'tele_app_ids': tele_app_ids,
            'missed_medicines_ids': missed_medicines_ids,
            'cancel_medicines_ids': cancel_medicines_ids,
            'tele_app_con_ids': tele_app_con_ids,
            'my_tele_sch_con_ids': my_tele_sch_con_ids,
            'hvd_app_sch_ids': hvd_app_sch_ids,
            'hvd_app_con_ids': hvd_app_con_ids,
            'my_hvd_sch_con_ids': my_hvd_sch_con_ids,
            'physiotherapy_app_sc_ids': physiotherapy_app_sc_ids,
            'physiotherapy_app_co_ids': physiotherapy_app_co_ids,
            'physiotherapy_app_op_ids': physiotherapy_app_op_ids,
            'physiotherapy_app_tm_ids': physiotherapy_app_tm_ids,
            'physiotherapy_app_inp_ids': physiotherapy_app_inp_ids,
            'physiotherapy_app_vd_ids': physiotherapy_app_vd_ids,
            'physiotherapy_app_ca_ids': physiotherapy_app_ca_ids,
            'my_phy_all_ids': my_phy_all_ids,
            'hhc_app_sch_ids': hhc_app_sch_ids,
            'hhc_app_hd_ids': hhc_app_hd_ids,
            'hhc_app_hn_ids': hhc_app_hn_ids,
            'hhc_app_om_ids': hhc_app_om_ids,
            'hhc_app_tm_ids': hhc_app_tm_ids,
            'my_hhc_sch_all_ids': my_hhc_sch_all_ids,
            'my_tele_today_ids': my_tele_today_ids,
            'my_hvd_today_ids': my_hvd_today_ids,
            'my_hhc_today_ids': my_hhc_today_ids,
            'my_phy_today_ids': my_phy_today_ids,
            'my_pcr_today_ids': my_pcr_today_ids,
            'pcr_app_sch_ids': pcr_app_sch_ids,
            'pcr_app_opm_ids': pcr_app_opm_ids,
            'pcr_app_tm_ids': pcr_app_tm_ids,
            'my_pcr_all_ids': my_pcr_all_ids,
            'service_request_ids': service_request_ids,
            'notification_ids': notification_ids,
            'image_request_ids': image_request_ids,
            'lab_request_ids': lab_request_ids,
            'investigation_ids': investigation_ids,
            'referral_ids': referral_ids,
            'requested_payments_ids': requested_payments_ids,
            'requested_payments_send_ids': requested_payments_send_ids,
            'requested_payments_paid_ids': requested_payments_paid_ids,
            'cancellation_refund_ids': cancellation_refund_ids,
            'cancellation_refund_pr_ids': cancellation_refund_pr_ids,
            'cancellation_refund_op_ids': cancellation_refund_op_ids,
            'hhc_tod_tm_res_the_ids': hhc_tod_tm_res_the_ids,
            'tele_tod_tm_res_the_ids': tele_tod_tm_res_the_ids,
            'hhc_tod_tm_soc_wor_ids': hhc_tod_tm_soc_wor_ids,
            'tele_tod_con_soc_wor_ids': tele_tod_con_soc_wor_ids,
            'hhc_tod_tm_hhc_nurse_ids': hhc_tod_tm_hhc_nurse_ids,
            'tele_tod_con_hhc_nurse_ids': tele_tod_con_hhc_nurse_ids,
            'pcr_tod_tm_hhc_nurse_ids': pcr_tod_tm_hhc_nurse_ids,
            'pcr_tod_tm_lab_technician_ids': pcr_tod_tm_lab_technician_ids,
            'phy_tod_tm_hhc_phy_ids': phy_tod_tm_hhc_phy_ids,
            'hhc_tod_tm_hhc_phy_ids': hhc_tod_tm_hhc_phy_ids,
            'tele_tod_con_hhc_phy_ids': tele_tod_con_hhc_phy_ids,
            'tele_tod_con_tele_app_ids': tele_tod_con_tele_app_ids,
            'hhc_tod_tm_hhc_doctor_ids': hhc_tod_tm_hhc_doctor_ids,
            'tele_tod_con_hhc_doctor_ids': tele_tod_con_hhc_doctor_ids,
            'hvd_tod_con_hhc_doctor_ids': hvd_tod_con_hhc_doctor_ids,
            'tele_tod_con_head_phy_ids': tele_tod_con_head_phy_ids,
            'hhc_tod_tm_head_phy_ids': hhc_tod_tm_head_phy_ids,
            'phy_tod_tm_head_phy_ids': phy_tod_tm_head_phy_ids,
            'hhc_tod_tm_head_nurse_ids': hhc_tod_tm_head_nurse_ids,
            'pcr_tod_tm_head_nurse_ids': pcr_tod_tm_head_nurse_ids,
            'hvd_tod_con_head_doctor_ids': hvd_tod_con_head_doctor_ids,
            'hhc_tod_tm_head_doctor_ids': hhc_tod_tm_head_doctor_ids,
            'call_center_ids': call_center_ids,
            'call_center_op_ids': call_center_op_ids,
            'hhc_app_vd_ids': hhc_app_vd_ids,
            'hhc_app_inp_ids': hhc_app_inp_ids,
            'hhc_app_ca_ids': hhc_app_ca_ids,
            'web_req_ids': web_req_ids,

            'my_physiotherapy_app_tm_ids': my_physiotherapy_app_tm_ids,
            'my_hhc_app_tm_ids': my_hhc_app_tm_ids,
            'my_hhc_app_phy_tm_ids': my_hhc_app_phy_tm_ids,
            'my_physiotherapy_app_sch_ids': my_physiotherapy_app_sch_ids,
            'my_physiotherapy_app_hp_ids': my_physiotherapy_app_hp_ids,
            'my_physiotherapy_app_op_ids': my_physiotherapy_app_op_ids,
            'my_h_hhc_app_tm_ids': my_h_hhc_app_tm_ids,
            'my_tele_app_con_ids': my_tele_app_con_ids,
            'my_tele_app_hn_con_ids': my_tele_app_hn_con_ids,
            'my_tele_app_hdphy_con_ids': my_tele_app_hdphy_con_ids,
            'my_tele_app_hhcn_con_ids': my_tele_app_hhcn_con_ids,
            'my_hhcn_pcr_app_tm_ids': my_hhcn_pcr_app_tm_ids,
            'my_tele_app_hhcphy_con_ids': my_tele_app_hhcphy_con_ids,
            'my_hvd_app_con_ids': my_hvd_app_con_ids,
            'my_rh_hhc_app_tm_ids': my_rh_hhc_app_tm_ids,
            'my_rh_tele_app_con_ids': my_rh_tele_app_con_ids,
            'my_rh_hvd_app_con_ids': my_rh_hvd_app_con_ids,

            # Sleep Medicine Request
            'slep_me_req_unpaid_ids': slep_me_req_unpaid_ids,
            'slep_me_req_paid_ids': slep_me_req_paid_ids,
            'slep_me_req_ev_ids': slep_me_req_ev_ids,
            'slep_me_req_sch_ids': slep_me_req_sch_ids,
            # Caregiver Contract
            'car_cont_unpaid_ids': car_cont_unpaid_ids,
            'car_cont_paid_ids': car_cont_paid_ids,
            'car_cont_ev_ids': car_cont_ev_ids,
            'car_cont_as_car_ids': car_cont_as_car_ids,
            'car_cont_act_ids': car_cont_act_ids,
            'car_cont_hrq_ids': car_cont_hrq_ids,
            'car_cont_trq_ids': car_cont_trq_ids,
            'car_cont_rew_ids': car_cont_rew_ids,
            'car_cont_hol_ids': car_cont_hol_ids,
            'car_cont_rea_req_ids': car_cont_rea_req_ids,

            'hhc_app_cr_ids': hhc_app_cr_ids,
            'phy_app_cr_ids': phy_app_cr_ids,
            'draft_payment_ids': draft_payment_ids,

        }
        return data

    # Filter All Data Till Now
    @api.model
    def sm_data_now(self):
        filter_type = 'till_now'
        tele_app_ids = self.get_data_count_filter(filter_type, 'oeh_medical_appointment', 'Scheduled')
        missed_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'missed')
        cancel_medicines_ids = self.get_data_count_filter('till_now', 'sm_caregiver_medicine_schedule', 'canceled')
        tele_app_con_ids = self.get_data_count_filter(filter_type, 'oeh_medical_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_tele_sch_con_ids = self.get_data_appointment_count_filter(filter_type, 'oeh_medical_appointment', states)
        hvd_app_sch_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 'Scheduled')
        hvd_app_con_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 'Confirmed')
        states = "'Scheduled', 'Confirmed'"
        my_hvd_sch_con_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_hvd_appointment', states)
        physiotherapy_app_sc_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                              'scheduled')
        physiotherapy_app_co_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                              'head_physiotherapist')
        physiotherapy_app_op_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                              'operation_manager')
        physiotherapy_app_tm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment', 'team')
        physiotherapy_app_inp_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                               'in_progress')
        physiotherapy_app_vd_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                              'visit_done')
        physiotherapy_app_ca_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                              'canceled')
        states = "'scheduled', 'head_physiotherapist', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_phy_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                states)
        hhc_app_sch_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'scheduled')
        hhc_app_hd_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'head_doctor')
        hhc_app_hn_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'head_nurse')
        hhc_app_om_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'operation_manager')
        hhc_app_tm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'team')
        states = "'scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team', 'in_progress', 'visit_done', 'canceled'"
        my_hhc_sch_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_hhc_appointment', states)
        tele_state = "'Scheduled', 'Confirmed', 'Start'"
        my_tele_today_ids = self.get_count_data_appointment_filter(filter_type, 'oeh_medical_appointment', tele_state)
        hvd_state = "'Scheduled', 'Confirmed', 'Start'"
        my_hvd_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hvd_appointment', hvd_state)
        hhc_state = "'scheduled','head_doctor','head_nurse','operation_manager','team','in_progress','visit_done','canceled'"
        my_hhc_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_hhc_appointment', hhc_state)
        phy_state = "'scheduled','head_physiotherapist','operation_manager','team','in_progress','canceled','visit_done'"
        my_phy_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                  phy_state)
        pcr_state = "'scheduled','operation_manager','team','in_progress','canceled','visit_done'"
        my_pcr_today_ids = self.get_count_data_appointment_filter(filter_type, 'sm_shifa_pcr_appointment', pcr_state)
        pcr_app_sch_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'scheduled')
        pcr_app_opm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'operation_manager')
        pcr_app_tm_ids = self.get_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 'team')
        states = "'scheduled', 'operation_manager', 'team'"
        my_pcr_all_ids = self.get_data_appointment_count_filter(filter_type, 'sm_shifa_pcr_appointment', states)
        service_request_ids = self.get_data_count_filter('till_now', 'sm_shifa_service_request', 'received')
        # service_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_service_request', 'received')
        noti_states = "'Start', 'Send'"
        notification_ids = self.get_data_multistate_count_filter('till_now', 'sm_physician_notification', noti_states)
        # notification_ids = self.get_data_count_filter(filter_type, 'sm_physician_notification', 'Send')
        image_states = "'Call Center', 'Team'"
        image_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_imaging_request', image_states)
        # image_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_imaging_request', 'Call Center')
        lab_states = "'Call Center', 'Team'"
        lab_request_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_lab_request', lab_states)
        # lab_request_ids = self.get_data_count_filter(filter_type, 'sm_shifa_lab_request', 'Call Center')
        investigation_states = "'Draft', 'Call Center', 'Team'"
        investigation_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_investigation',
                                                                  investigation_states)
        # investigation_ids = self.get_data_count_filter(filter_type, 'sm_shifa_investigation', 'Call Center')
        referral_states = "'start', 'call_center'"
        referral_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_referral', referral_states)
        # referral_ids = self.get_data_count_filter(filter_type, 'sm_shifa_referral', 'call_center')
        pay_states = "'Start', 'Send'"
        # requested_payments_ids = self.get_data_multistate_count_filter('till_now', 'sm_shifa_requested_payments', pay_states)
        requested_payments_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Start')
        requested_payments_send_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Send')
        requested_payments_paid_ids = self.get_data_count_filter('till_now', 'sm_shifa_requested_payments', 'Paid')
        cancel_states = "'received', 'operation_manager', 'Processed'"
        # cancellation_refund_ids = self.get_data_multistate_count_filter(filter_type, 'sm_shifa_cancellation_refund', cancel_states)
        cancellation_refund_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'received')
        cancellation_refund_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund',
                                                                'operation_manager')
        cancellation_refund_pr_ids = self.get_data_count_filter('till_now', 'sm_shifa_cancellation_refund', 'Processed')
        hhc_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type,
                                                                              'sm_shifa_hhc_appointment',
                                                                              'team')
        tele_tod_tm_res_the_ids = self.get_today_data_appointment_count_filter(filter_type, 'oeh_medical_appointment',
                                                                               'Confirmed')
        hhc_tod_tm_soc_wor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_hhc_appointment',
                                                                                   't.social_worker', 'team')
        tele_tod_con_soc_wor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_nurse_ids = self.get_all_clinicians_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hhc_appointment',
                                                                                         'team')
        tele_tod_con_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor',
                                                                                       'Confirmed')
        pcr_tod_tm_hhc_nurse_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_pcr_appointment',
                                                                                     't.nurse', 'team')
        pcr_tod_tm_lab_technician_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                          'sm_shifa_pcr_appointment',
                                                                                          't.lab_technician', 'team')
        phy_tod_tm_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_physiotherapy_appointment',
                                                                                   't.physiotherapist', 'team')
        hhc_tod_tm_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                   'sm_shifa_hhc_appointment',
                                                                                   't.physiotherapist', 'team')
        tele_tod_con_hhc_phy_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                     'oeh_medical_appointment',
                                                                                     't.doctor', 'Confirmed')
        tele_tod_con_tele_app_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                      'oeh_medical_appointment',
                                                                                      't.doctor', 'Confirmed')
        hhc_tod_tm_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                      'sm_shifa_hhc_appointment',
                                                                                      't.doctor', 'team')
        tele_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                        'oeh_medical_appointment',
                                                                                        't.doctor', 'Confirmed')
        hvd_tod_con_hhc_doctor_ids = self.get_user_today_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_hvd_appointment',
                                                                                       't.doctor', 'Confirmed')
        tele_tod_con_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'oeh_medical_appointment',
                                                                                       't.doctor', tele_state)
        hhc_tod_tm_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_hhc_appointment',
                                                                                     't.physiotherapist', hhc_state)
        phy_tod_tm_head_phy_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                     'sm_shifa_physiotherapy_appointment',
                                                                                     't.physiotherapist', phy_state)
        hhc_tod_tm_head_nurse_ids = self.get_all_clinicians_urgent_data_appointment_count_filter(filter_type,
                                                                                                 'sm_shifa_hhc_appointment',
                                                                                                 hhc_state)
        pcr_tod_tm_head_nurse_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                       'sm_shifa_pcr_appointment',
                                                                                       't.nurse', pcr_state)
        hvd_tod_con_head_doctor_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                         'sm_shifa_hvd_appointment',
                                                                                         't.doctor', hvd_state)
        hhc_tod_tm_head_doctor_ids = self.get_user_urgent_data_appointment_count_filter(filter_type,
                                                                                        'sm_shifa_hhc_appointment',
                                                                                        't.doctor', hhc_state)

        my_physiotherapy_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'team')
        my_physiotherapy_app_sch_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                     't.physiotherapist', 'scheduled')
        my_physiotherapy_app_hp_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'head_physiotherapist')
        my_physiotherapy_app_op_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                                    't.physiotherapist', 'operation_manager')
        my_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.nurse', 'team')
        my_hhc_app_phy_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment',
                                                              't.physiotherapist', 'team')
        my_h_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                            'team')
        my_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                            'Confirmed')
        my_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                           'Confirmed')
        my_tele_app_hn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_tele_app_hdphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                  'Confirmed')
        my_tele_app_hhcn_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                 'Confirmed')
        my_hhcn_pcr_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_pcr_appointment', 't.nurse',
                                                               'team')
        my_tele_app_hhcphy_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                                   'Confirmed')
        my_rh_hhc_app_tm_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 't.head_doctor',
                                                             'team')
        my_rh_tele_app_con_ids = self.get_my_data_count_filter(filter_type, 'oeh_medical_appointment', 't.doctor',
                                                               'Confirmed')
        my_rh_hvd_app_con_ids = self.get_my_data_count_filter(filter_type, 'sm_shifa_hvd_appointment', 't.doctor',
                                                              'Confirmed')
        call_center_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'call_center')
        call_center_op_ids = self.get_data_count_filter('till_now', 'sm_shifa_call_center_census', 'operation_manager')
        hhc_app_vd_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'visit_done')
        hhc_app_inp_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'in_progress')
        hhc_app_ca_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'canceled')
        web_req_ids = self.get_data_count_filter('till_now', 'sm_shifa_web_request', 'Received')

        # Sleep Medicine Request
        slep_me_req_unpaid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'unpaid')
        slep_me_req_paid_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'paid')
        slep_me_req_ev_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'evaluation')
        slep_me_req_sch_ids = self.get_data_count_filter('till_now', 'sm_sleep_medicine_request', 'scheduling')
        # Caregiver Contract
        car_cont_unpaid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'unpaid')
        car_cont_paid_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'paid')
        car_cont_ev_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'evaluation')
        car_cont_as_car_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'assign_caregiver')
        car_cont_act_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'active')
        car_cont_hrq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'holdreq')
        car_cont_trq_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'terminationreq')
        car_cont_rew_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'renew')
        car_cont_hol_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'hold')
        car_cont_rea_req_ids = self.get_data_count_filter('till_now', 'sm_caregiver_contracts', 'reactivation_request')

        hhc_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_hhc_appointment', 'requestCancellation')
        phy_app_cr_ids = self.get_data_count_filter(filter_type, 'sm_shifa_physiotherapy_appointment',
                                                    'requestCancellation')

        draft_payment_ids = self.get_data_count_from_odoo_payment('draft')

        data = {
            'tele_app_ids': tele_app_ids,
            'missed_medicines_ids': missed_medicines_ids,
            'cancel_medicines_ids': cancel_medicines_ids,
            'tele_app_con_ids': tele_app_con_ids,
            'my_tele_sch_con_ids': my_tele_sch_con_ids,
            'hvd_app_sch_ids': hvd_app_sch_ids,
            'hvd_app_con_ids': hvd_app_con_ids,
            'my_hvd_sch_con_ids': my_hvd_sch_con_ids,
            'physiotherapy_app_sc_ids': physiotherapy_app_sc_ids,
            'physiotherapy_app_co_ids': physiotherapy_app_co_ids,
            'physiotherapy_app_op_ids': physiotherapy_app_op_ids,
            'physiotherapy_app_tm_ids': physiotherapy_app_tm_ids,
            'physiotherapy_app_inp_ids': physiotherapy_app_inp_ids,
            'physiotherapy_app_vd_ids': physiotherapy_app_vd_ids,
            'physiotherapy_app_ca_ids': physiotherapy_app_ca_ids,
            'my_phy_all_ids': my_phy_all_ids,
            'hhc_app_sch_ids': hhc_app_sch_ids,
            'hhc_app_hd_ids': hhc_app_hd_ids,
            'hhc_app_hn_ids': hhc_app_hn_ids,
            'hhc_app_om_ids': hhc_app_om_ids,
            'hhc_app_tm_ids': hhc_app_tm_ids,
            'my_hhc_sch_all_ids': my_hhc_sch_all_ids,
            'my_tele_today_ids': my_tele_today_ids,
            'my_hvd_today_ids': my_hvd_today_ids,
            'my_hhc_today_ids': my_hhc_today_ids,
            'my_phy_today_ids': my_phy_today_ids,
            'my_pcr_today_ids': my_pcr_today_ids,
            'pcr_app_sch_ids': pcr_app_sch_ids,
            'pcr_app_opm_ids': pcr_app_opm_ids,
            'pcr_app_tm_ids': pcr_app_tm_ids,
            'my_pcr_all_ids': my_pcr_all_ids,
            'service_request_ids': service_request_ids,
            'notification_ids': notification_ids,
            'image_request_ids': image_request_ids,
            'lab_request_ids': lab_request_ids,
            'investigation_ids': investigation_ids,
            'referral_ids': referral_ids,
            'requested_payments_ids': requested_payments_ids,
            'requested_payments_send_ids': requested_payments_send_ids,
            'requested_payments_paid_ids': requested_payments_paid_ids,
            'cancellation_refund_ids': cancellation_refund_ids,
            'cancellation_refund_pr_ids': cancellation_refund_pr_ids,
            'cancellation_refund_op_ids': cancellation_refund_op_ids,
            'hhc_tod_tm_res_the_ids': hhc_tod_tm_res_the_ids,
            'tele_tod_tm_res_the_ids': tele_tod_tm_res_the_ids,
            'hhc_tod_tm_soc_wor_ids': hhc_tod_tm_soc_wor_ids,
            'tele_tod_con_soc_wor_ids': tele_tod_con_soc_wor_ids,
            'hhc_tod_tm_hhc_nurse_ids': hhc_tod_tm_hhc_nurse_ids,
            'tele_tod_con_hhc_nurse_ids': tele_tod_con_hhc_nurse_ids,
            'pcr_tod_tm_hhc_nurse_ids': pcr_tod_tm_hhc_nurse_ids,
            'pcr_tod_tm_lab_technician_ids': pcr_tod_tm_lab_technician_ids,
            'phy_tod_tm_hhc_phy_ids': phy_tod_tm_hhc_phy_ids,
            'hhc_tod_tm_hhc_phy_ids': hhc_tod_tm_hhc_phy_ids,
            'tele_tod_con_hhc_phy_ids': tele_tod_con_hhc_phy_ids,
            'tele_tod_con_tele_app_ids': tele_tod_con_tele_app_ids,
            'hhc_tod_tm_hhc_doctor_ids': hhc_tod_tm_hhc_doctor_ids,
            'tele_tod_con_hhc_doctor_ids': tele_tod_con_hhc_doctor_ids,
            'hvd_tod_con_hhc_doctor_ids': hvd_tod_con_hhc_doctor_ids,
            'tele_tod_con_head_phy_ids': tele_tod_con_head_phy_ids,
            'hhc_tod_tm_head_phy_ids': hhc_tod_tm_head_phy_ids,
            'phy_tod_tm_head_phy_ids': phy_tod_tm_head_phy_ids,
            'hhc_tod_tm_head_nurse_ids': hhc_tod_tm_head_nurse_ids,
            'pcr_tod_tm_head_nurse_ids': pcr_tod_tm_head_nurse_ids,
            'hvd_tod_con_head_doctor_ids': hvd_tod_con_head_doctor_ids,
            'hhc_tod_tm_head_doctor_ids': hhc_tod_tm_head_doctor_ids,
            'call_center_ids': call_center_ids,
            'call_center_op_ids': call_center_op_ids,
            'hhc_app_vd_ids': hhc_app_vd_ids,
            'hhc_app_inp_ids': hhc_app_inp_ids,
            'hhc_app_ca_ids': hhc_app_ca_ids,
            'web_req_ids': web_req_ids,

            'my_physiotherapy_app_tm_ids': my_physiotherapy_app_tm_ids,
            'my_hhc_app_tm_ids': my_hhc_app_tm_ids,
            'my_hhc_app_phy_tm_ids': my_hhc_app_phy_tm_ids,
            'my_physiotherapy_app_sch_ids': my_physiotherapy_app_sch_ids,
            'my_physiotherapy_app_hp_ids': my_physiotherapy_app_hp_ids,
            'my_physiotherapy_app_op_ids': my_physiotherapy_app_op_ids,
            'my_h_hhc_app_tm_ids': my_h_hhc_app_tm_ids,
            'my_tele_app_con_ids': my_tele_app_con_ids,
            'my_hvd_app_con_ids': my_hvd_app_con_ids,
            'my_tele_app_hn_con_ids': my_tele_app_hn_con_ids,
            'my_tele_app_hdphy_con_ids': my_tele_app_hdphy_con_ids,
            'my_tele_app_hhcn_con_ids': my_tele_app_hhcn_con_ids,
            'my_hhcn_pcr_app_tm_ids': my_hhcn_pcr_app_tm_ids,
            'my_tele_app_hhcphy_con_ids': my_tele_app_hhcphy_con_ids,
            'my_rh_hhc_app_tm_ids': my_rh_hhc_app_tm_ids,
            'my_rh_tele_app_con_ids': my_rh_tele_app_con_ids,
            'my_rh_hvd_app_con_ids': my_rh_hvd_app_con_ids,
            # Sleep Medicine Request
            'slep_me_req_unpaid_ids': slep_me_req_unpaid_ids,
            'slep_me_req_paid_ids': slep_me_req_paid_ids,
            'slep_me_req_ev_ids': slep_me_req_ev_ids,
            'slep_me_req_sch_ids': slep_me_req_sch_ids,
            # Caregiver Contract
            'car_cont_unpaid_ids': car_cont_unpaid_ids,
            'car_cont_paid_ids': car_cont_paid_ids,
            'car_cont_ev_ids': car_cont_ev_ids,
            'car_cont_as_car_ids': car_cont_as_car_ids,
            'car_cont_act_ids': car_cont_act_ids,
            'car_cont_hrq_ids': car_cont_hrq_ids,
            'car_cont_trq_ids': car_cont_trq_ids,
            'car_cont_rew_ids': car_cont_rew_ids,
            'car_cont_hol_ids': car_cont_hol_ids,
            'car_cont_rea_req_ids': car_cont_rea_req_ids,

            'hhc_app_cr_ids': hhc_app_cr_ids,
            'phy_app_cr_ids': phy_app_cr_ids,
            'draft_payment_ids': draft_payment_ids,
        }
        return data
