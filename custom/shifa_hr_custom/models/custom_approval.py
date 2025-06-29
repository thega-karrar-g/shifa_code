from odoo import models, fields, api, _

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    _description = "inherited from hrm/employee_approvals/model/approval_category"

    name = fields.Selection(
        selection=[
            ('renew_iqama', _('Renew Iqama / تجديد الإقامة')),
            ('clearance_procedure', _('Clearance Procedure / إخلاء طرف')),
            ('budget', _('Budget Approval / الموافقة على الميزانية')),
            ('resignation_request', _('Resignation Request / طلب استقالة'))
        ],
        string="Name",
        required=True,
    )




 