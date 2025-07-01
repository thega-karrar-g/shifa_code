from odoo import models, fields, api
from datetime import date, datetime, timedelta
import calendar


class SMDashboard(models.Model):
    _name = 'sm.insurance.dashboard'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    dashboard_user_id = fields.Many2one("res.users", string="Dashboard User", store=True)

    @api.model
    def login_user_img_url(self):
        """
        Overall, this function facilitates obtaining the URL for the logged-in user's profile image,
        along with their name, in an Odoo system.
        :return: Return the user's image URL and name
        """
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        login_user = self.env.user.id
        login_name = self.env.user.name
        img_url = config_obj + "/web/image?model=res.users&field=image_128&id=" + str(login_user)
        data = {
            'img_url': img_url,
            'name': login_name
        }
        return data

    @api.model
    def login_user_group(self):
        """
            Determines the group or role of the currently logged-in user.

            Returns:
                int: The group identifier based on the user's role.
            """
        login_user = self.env.user
        self.login_user_img_url()
        if login_user.has_group('sm_configuration.group_reayah_admin'):
            return 1

        elif login_user.has_group('sm_configuration.group_reayah_physician'):
            return 2
        elif login_user.has_group('sm_configuration.group_reayah_operation_manager'):
            return 3



    def get_data_ids(self, filter_type, table, state_val):
        current_company_id = self.env.user.company_id.id
        if filter_type == 'today':
            query = """
                SELECT id 
                FROM {0} 
                WHERE create_date::date = '{1}'::date
                AND state = '{2}' 
                AND active = True
                AND company_id = {3}
            """.format(table, date.today(), state_val, current_company_id)
            self._cr.execute(query)
            record = self._cr.fetchall()
            today_ids = [item[0] for item in record]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids

        elif filter_type == 'week':
            today = date.today()
            start_day = today - timedelta(days=today.weekday())
            end_day = start_day + timedelta(days=6)
            query = """
                SELECT id 
                FROM {0} 
                WHERE create_date::date >= '{1}'::date 
                AND create_date::date <= '{2}'::date 
                AND state = '{3}' 
                AND active = True
                AND company_id = {4}
            """.format(table, start_day, end_day, state_val, current_company_id)
            self._cr.execute(query)
            record = self._cr.fetchall()
            week_ids = [item[0] for item in record]
            week_ids.insert(0, len(week_ids))
            return week_ids

        elif filter_type == 'month':
            today = date.today()
            this_month = today.month
            this_year = today.year
            last_day = calendar.monthrange(this_year, this_month)[1]
            this_month_fst_date = date(this_year, this_month, 1)
            this_month_snd_date = date(this_year, this_month, last_day)
            query = """
                SELECT id 
                FROM {0} 
                WHERE create_date::date BETWEEN '{1}'::date AND '{2}'::date 
                AND state = '{3}' 
                AND active = True
                AND company_id = {4}
            """.format(table, this_month_fst_date, this_month_snd_date, state_val, current_company_id)
            self._cr.execute(query)
            record = self._cr.fetchall()
            month_ids = [item[0] for item in record]
            month_ids.insert(0, len(month_ids))
            return month_ids

        elif filter_type == 'till_now':
            query = """
                SELECT id 
                FROM {0} 
                WHERE state = '{1}' 
                AND active = True
                AND company_id = {2}
            """.format(table, state_val, current_company_id)
            self._cr.execute(query)
            record = self._cr.fetchall()
            all_ids = [item[0] for item in record]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    def get_create_date_data_ids(self, filter_type, table, state_val):
        if filter_type == 'today':
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) = cast('{1}' as Date) and state = '{2}'".format(
                    table, date.today().strftime("%Y-%m-%d"), state_val))
            record = self._cr.fetchall()
            today_ids = [item for t in record for item in t]
            count = len(today_ids)
            today_ids.insert(0, count)
            return today_ids
        elif filter_type == 'week':
            day = date.today()
            dt = datetime.strptime(str(day), '%Y-%m-%d')
            start_day = dt - timedelta(days=dt.weekday())
            end_day = start_day + timedelta(days=6)
            start_day = start_day.strftime("%Y-%m-%d")
            end_day = end_day.strftime("%Y-%m-%d")
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) >= cast('{1}' as Date) AND cast(create_date as Date) <= cast('{2}' as Date) and state = '{3}'".format(
                    table, start_day, end_day, state_val))
            record = self._cr.fetchall()
            week_ids = [item for t in record for item in t]
            week_ids.insert(0, len(week_ids))
            return week_ids
        elif filter_type == 'month':
            curr_month = datetime.now().month
            curr_year = datetime.now().year
            last_day = calendar.monthrange(curr_year, curr_month)[1]
            curr_month_first_dt = str(curr_year) + '-' + str(curr_month) + '-1'
            curr_month_last_dt = str(curr_year) + '-' + str(curr_month) + '-' + str(last_day)
            self._cr.execute(
                "select id from {0} WHERE cast(create_date as Date) between cast('{1}' as Date) and cast('{2}' as Date) and state = '{3}'".format(
                    table, curr_month_first_dt, curr_month_last_dt, state_val))
            record = self._cr.fetchall()
            month_ids = [item for t in record for item in t]
            month_ids.insert(0, len(month_ids))
            return month_ids
        elif filter_type == 'till_now':
            self._cr.execute(
                "select id from {0} where state = '{1}'".format(table, state_val))
            record = self._cr.fetchall()
            all_ids = [item for t in record for item in t]
            count = len(all_ids)
            all_ids.insert(0, count)
            return all_ids

    @api.model
    def sm_data_today(self):
        """
        Retrieve data for today's date.
        :return: A dictionary containing the data.
        """
        filter_type = 'today'




        eligibility_request_sent_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'sent')
        eligibility_request_processed_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'processed')
        authorization_request_sent_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'sent')
        authorization_request_processed_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'processed')


        data = {

            'eligibility_request_sent_ids': eligibility_request_sent_ids,
            'eligibility_request_processed_ids': eligibility_request_processed_ids,
            'authorization_request_sent_ids': authorization_request_sent_ids,
            'authorization_request_processed_ids': authorization_request_processed_ids,


        }
        return data

    @api.model
    def sm_data_week(self):
        """
        Retrieve data for this week's date.
        :return: A dictionary containing the data.
        """
        filter_type = 'week'

        eligibility_request_sent_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'sent')
        eligibility_request_processed_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'processed')
        authorization_request_sent_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'sent')
        authorization_request_processed_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'processed')






        data = {

            'eligibility_request_sent_ids': eligibility_request_sent_ids,
            'eligibility_request_processed_ids': eligibility_request_processed_ids,
            'authorization_request_sent_ids': authorization_request_sent_ids,
            'authorization_request_processed_ids': authorization_request_processed_ids,

        }
        return data

    @api.model
    def sm_data_month(self):
        """
        Retrieve data for all.
        :return: A dictionary containing the data.
        """
        filter_type = 'month'

        eligibility_request_sent_ids = self.get_data_ids('month', 'sm_eligibility_check_request', 'sent')
        eligibility_request_processed_ids = self.get_data_ids('month', 'sm_eligibility_check_request', 'processed')
        authorization_request_sent_ids = self.get_data_ids('month', 'sm_pre_authorization_request', 'sent')
        authorization_request_processed_ids = self.get_data_ids('month', 'sm_pre_authorization_request', 'processed')





        data = {
            'eligibility_request_sent_ids': eligibility_request_sent_ids,
            'eligibility_request_processed_ids': eligibility_request_processed_ids,
            'authorization_request_sent_ids': authorization_request_sent_ids,
            'authorization_request_processed_ids': authorization_request_processed_ids,

        }
        return data

    @api.model
    def sm_data_now(self):
        """
        Retrieve data for all.
        :return: A dictionary containing the data.
        """
        filter_type = 'till_now'


        eligibility_request_sent_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'sent')
        eligibility_request_processed_ids = self.get_data_ids(filter_type, 'sm_eligibility_check_request', 'processed')
        authorization_request_sent_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'sent')
        authorization_request_processed_ids = self.get_data_ids(filter_type, 'sm_pre_authorization_request', 'processed')




        data = {

            'eligibility_request_sent_ids': eligibility_request_sent_ids,
            'eligibility_request_processed_ids': eligibility_request_processed_ids,
            'authorization_request_sent_ids': authorization_request_sent_ids,
            'authorization_request_processed_ids': authorization_request_processed_ids,

        }
        return data
