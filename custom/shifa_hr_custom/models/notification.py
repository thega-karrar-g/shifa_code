from datetime import timedelta
from odoo import api, fields, models

class Notification(models.Model):
    _inherit = 'hr.employee'
    _description = "Extended to send Iqama expiry alerts"

    @api.model
    def _get_expire_iqama(self): 
        today = fields.Date.today()
        limit_date = today + timedelta(days=30)
        print(today)
        expiring_employees = self.search([
            ('identification_end_date', '>=', today),
            ('identification_end_date', '<=', limit_date),
            ])
        if not expiring_employees:
            return

        group = self.env.ref('shifa_hr_custom.group_hr_manager_notification', raise_if_not_found=False)
        if not group:
            return
            users = group.users.filtered(lambda u: u.email)
            print("users")
            print(users)
            if not users:
                return
                emails = ",".join(users.mapped('email'))
                body = """
                <div style="font-family:Arial, sans-serif; color:#b71c1c;">
                <h2 style="color:#b71c1c;">URGENT: Employee Iqama Expiry Warning ⚠️</h2>
                <p>The following employees have <strong>Iqama documents expiring within 30 days</strong>:</p>
                <ul style="color:#000000;">
                """
                for emp in expiring_employees:
                    expiry_str = emp.identification_end_date.strftime("%Y-%m-%d")
                    body += f"<li><strong>{emp.name}</strong> – Iqama Expiry Date: <strong>{expiry_str}</strong></li>"
                    self.env['mail.mail'].create({
                        'subject': '⚠️ URGENT: Iqama Expiry Alert / انتهاء اقامة موظفين خلال 30 يوم',
                        'body_html': body,
                        'email_to': emails,
                        }).send()




























# from datetime import timedelta
# from odoo import api, fields, models

# class Notification(models.Model):
#     _inherit = 'hr.employee'
#     _description = "Extended to send Iqama expiry alerts"

#     @api.model
#     def _get_expire_iqama(self):
#         today = fields.Date.today()
#         target_date = today + timedelta(days=5)

#         expiring_employees = self.search([
#             ('identification_end_date', '=', target_date)
#         ])

#         if not expiring_employees:
#             return

#         group = self.env.ref('shifa_hr_custom.group_hr_manager_notification', raise_if_not_found=False)
#         if not group:
#             return

#         users = group.users.filtered(lambda u: u.email)
#         if not users:
#             return

#         emails = ",".join(users.mapped('email'))

#         body = """
#         <div style="font-family:Arial, sans-serif; color:#b71c1c;">
#             <h2 style="color:#b71c1c;">⚠️ URGENT: Employee Iqama Expiry Warning ⚠️</h2>
#             <p>The following employees have <strong>Iqama documents expiring in 5 days</strong>:</p>
#             <ul style="color:#000000;">
#         """
#         for emp in expiring_employees:
#             expiry_str = emp.identification_end_date.strftime("%Y-%m-%d")
#             body += f"<li><strong>{emp.name}</strong> – Iqama Expiry Date: <strong>{expiry_str}</strong></li>"
#         body += """
#             </ul>
#             <p style="color:#b71c1c;"><strong>Action Required:</strong> Please renew these Iqamas immediately to ensure compliance with labor regulations.</p>
#         </div>
#         """

#         self.env['mail.mail'].create({
#             'subject': '⚠️ URGENT: Iqama Expiry Alert / انتهاء اقامة موظفين',
#             'body_html': body,
#             'email_to': emails,
#         }).send()
