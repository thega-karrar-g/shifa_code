from odoo import models, fields, api, _
from odoo.exceptions import UserError



class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    #_inherit = ['approval.request', 'mail.thread', 'mail.activity.mixin']

    request_status = fields.Selection([
        ('draft', 'Draft'),
        ('hr_approval', 'HR Approval'),
        ('finance', 'Finance'),
        ('operation', 'Operation'),
        ('sales', 'Sales'),
        ('it', 'IT'),
        ('gm', 'General Manager'),
        ('done', 'Done'),
    ], default='draft', string='Request Status', tracking=True)

    operation_comments = fields.Text(string='Operation Comments', tracking=True)
    sales_comments = fields.Text(string='Sales Comments', tracking=True)
    hr_comments = fields.Text(string='HR Comments', tracking=True)
    it_comments = fields.Text(string='IT Comments', tracking=True)
    gm_comments = fields.Text(string='GM Comments', tracking=True)
    finance_comments = fields.Text(string='Finance Comments', tracking=True)

    def action_hr_manager_approve(self):
        for order in self:
            order.request_status = 'hr_approval'
            order.message_post(body="Request HR Manager to approve request.")  # Chatter log

    def action_req_finance_manager_approve(self):
        for order in self:
            order.request_status = 'finance'
            order.message_post(body="Request Finance Manager to approve request.")  # Chatter log

    def action_req_operation_manager_approve(self):
        for order in self:
            order.request_status = 'operation'
            order.message_post(body="Finance Approved , Waiting for operation approved.")  # Chatter log

    def action_req_sales_manager_approve(self):
        for order in self:
            order.request_status = 'sales'
            order.message_post(body="operation Approved , Waiting for sales approved.")  # Chatter log

    def action_req_it_dept_approve(self):
        for order in self:
            order.request_status = 'it'
            order.message_post(body="sales Approved , Waiting for it approved.")  # Chatter log

    def action_req_gm_dept_approve(self):
        for order in self:
            order.request_status = 'gm'
            order.message_post(body="it Approved , Waiting for GM approved.")  # Chatter log

    def action_req_done_dept_approve(self):
        for order in self: 
            order.request_status = 'done'
            order.message_post(body="gm Approved ,Request completed.")  # Chatter log

    def action_send_to_maharah(self):
        group = self.env.ref('shifa_hr_custom.group_maharah_approval', raise_if_not_found=False)
        if not group:
            raise UserError(_("The group 'shifa_hr_custom.group_maharah_approval' was not found."))

        users = group.users.filtered(lambda u: u.email)
        if not users:
            raise UserError(_("No users with email found in Maharah group."))

        subject = "طلب إيقاف البريد الإلكتروني وسحب الرخصة"
        body = (
            "<div dir='rtl' style='text-align: right;'>"
            "مرحباً،<br/><br/>"
            "يرجى اتخاذ اللازم بشأن إيقاف البريد الإلكتروني وسحب الرخصة لهذا الطلب.<br/><br/>"
            f"<strong>الطلب:</strong> {self.name}<br/>"
            f"<strong>الموظف:</strong> {self.employee.sudo().name}<br/>"
            f"<strong>البريد الإلكتروني:</strong> {self.employee.sudo().work_email}<br/><br/>"
            "مع الشكر،<br/>"
            "</div>"
        )

        # Post to chatter with email delivery
        for user in users:
            self.message_post(
                body=body,
                subject=subject,
                message_type='email',
                subtype_id=self.env.ref('mail.mt_note').id,
                email_to=user.email,
            )

        return True


    # def action_send_to_maharah(self):
    #     # Get Maharah group
    #     #print(self)
    #     group = self.env.ref('shifa_hr_custom.group_maharah_approval', raise_if_not_found=False)
    #     if not group:
    #         raise UserError(_("The group 'shifa_hr_custom.group_maharah_approval' was not found."))

    #     # Get users in the group with email
    #     users = group.users.filtered(lambda u: u.email)
    #     if not users:
    #         raise UserError(_("No users with email found in Maharah group."))

    #     # Email subject and body
    #     #emp_name = self.env['hr.employee'].search([('id','=',self.employee.id)]).name

    #     #print('0000000000000000000000000000000',emp_name)
    #     subject = "طلب إيقاف البريد الإلكتروني وسحب الرخصة"
    #     body = (
    #         "<div dir='rtl' style='text-align: right;'>"
    #         "مرحباً،<br/><br/>"
    #         "يرجى اتخاذ اللازم بشأن إيقاف البريد الإلكتروني وسحب الرخصة لهذا الطلب.<br/><br/>"
    #         f"<strong>الطلب:</strong> {self.name}<br/>"
    #         f"<strong>الموظف:</strong> {self.employee.sudo().name}<br/>"
    #         f"<strong>البريد الإلكتروني:</strong> {self.employee.sudo().work_email}<br/><br/>"
    #         "مع الشكر،<br/>"
    #         "</div>"
    #     )

    #     # Send email to each user
    #     for user in users:
    #         self.env['mail.mail'].sudo().create({
    #             'subject': subject,
    #             'body_html': body,
    #             'email_to': user.email,
    #         }).send()

    #     return True


   








# from odoo import models, fields, _

# class ApprovalRequest(models.Model):
#     _inherit = 'approval.request'
#     _description = _("Extended Approval Request Model")

#     # request_status = fields.Selection([
#     #     ('draft', _('Draft')),
#     #     ('hr_approval', _('HR Approval')),
#     #     ('finance', _('Finance')),
#     #     ('operation', _('Operation')),
#     #     ('sales', _('Sales')),
#     #     ('it', _('IT')),
#     #     ('gm', _('General Manager')),
#     # ], default='draft', string=_('Request Status'))

#     request_status = fields.Selection(
#         [
#             ('draft', _('Draft')),
#             ('hr_approval', _('HR Approval')),
#             ('finance', _('Finance')),
#             ('operation', _('Operation')),
#             ('sales', _('Sales')),
#             ('it', _('IT')),
#             ('gm', _('General Manager')),
#         ],
#         default='draft',
#         string=_('Request Status'),
#         override=True  
#     )


#     operation_comments = fields.Text(string=_('Operation Comments'))
#     sales_comments = fields.Text(string=_('Sales Comments'))
#     hr_comments = fields.Text(string=_('HR Comments'))
#     gm_comments = fields.Text(string=_('GM Comments'))
#     it_comments = fields.Text(string=_('IT Comments'))
#     finance_comments = fields.Text(string=_('Finance Comments'))
