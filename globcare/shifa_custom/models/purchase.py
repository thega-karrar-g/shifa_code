from odoo import api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_description = fields.Char(string='Purchase Description')

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('manager_approval', 'Manager Approval'),
        ('general_manager_approval', 'General Manager Approval'),
        ('sent', 'RFQ Sent'),
        #('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def action_manager_approve(self):
        for order in self:
            order.state = 'manager_approval'

    def action_general_manager_approve(self):
        for order in self:
            order.state = 'general_manager_approval'

    def action_confirm_order_custom(self):
        for order in self:
            if order.state == 'general_manager_approval':
            # Call the standard Odoo confirm method
                # return super(PurchaseOrder, order).button_confirm()
                order._add_supplier_to_product()
                # Deal with double validation process
                if order._approval_allowed():
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
                if not order.requisition_id:
                    continue
                if order.requisition_id.type_id.exclusive == 'exclusive':
                    others_po = order.requisition_id.mapped('purchase_ids').filtered(lambda r: r.id != order.id)
                    others_po.button_cancel()
                    if order.state not in ['draft', 'sent', 'to approve']:
                        order.requisition_id.action_done()
                return True
            # raise UserError("You can't confirm this order yet.")

