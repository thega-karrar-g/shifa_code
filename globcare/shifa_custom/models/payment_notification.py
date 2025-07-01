from odoo import models, api

class CaregiverContract(models.Model):
    _inherit = "sm.caregiver.contracts"

    def test_print(self):
        print('-------------------------------------------------------')
        
    @api.model
    def _send_pending_payment_email(self):
        # Get all active contracts
        contracts = self.search([('state', '=', 'active')])
        pending_contracts = []

        for contract in contracts:
            # Collect and normalize states from requested payments
            request_payment_states = set(
                state.lower() for state in contract.request_payment_ids.mapped('state') if state
            )

            if any(state not in ['done', 'paid'] for state in request_payment_states):
                pending_contracts.append(contract.name)

        if pending_contracts:
            contract_list_html = "<br/>".join(f"- {name}" for name in pending_contracts)

            subject = "تنبيه بخصوص عقود نشطة لم تُسجّل لها مدفوعات"
            body = f"""
                مرحبًا فريق مركز الاتصال،<br/><br/>
                نود إعلامكم بأن العقود التالية في حالة <b>نشطة (Active)</b>،<br/>
                ولكن لم يتم تسجيل مدفوعات لها:<br/><br/>
                {contract_list_html}<br/><br/>
                يرجى التحقق واتخاذ الإجراءات اللازمة لضمان استكمال تسجيل المدفوعات.<br/><br/>
            """

            # Get all users in the group_hr_manager_notification group
            user_group = self.env.ref('shifa_custom.group_payment_notification')
            users = user_group.users.filtered(lambda u: u.email)

            email_to = ','.join(users.mapped('email'))

            if email_to:
                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': email_to,
                    'email_from': self.env.user.email or 'noreply@example.com',
                }).send()
