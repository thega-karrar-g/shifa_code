from odoo import api, fields, models
from odoo.exceptions import UserError

class RequestedPayment(models.Model):
    _inherit = "sm.shifa.requested.payments"
    _description = "for editing payment"

    date = fields.Date(
        string='Date',
        readonly=False,
        # states={
        #     'Start': [('readonly', False)],
        #     'Send': [('readonly', False)],
        # }
    )
    #date = fields.Date(string='Date', readonly=False, states={'Start': [('readonly', False)]})



