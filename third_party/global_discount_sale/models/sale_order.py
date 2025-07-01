# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class sale_order(models.Model):

    _inherit = "sale.order"

    discount_type = fields.Selection(
        [("fixed", "Fixed"), ("percentage", "Percentage")], string="Discount Type"
    )
    discount_amount = fields.Float("Discount Amount")
    discount = fields.Float("Discount", compute="_calculate_discount", store=True)

    @api.depends("discount_amount", "discount_type")
    def _calculate_discount(self):
        for rec in self:
            if rec.discount_amount < 0:
                raise UserError(
                    _(
                        "Discount Amount Must be zero OR grater than zero OR positive amount"
                    )
                )
            elif rec.discount_type == "fixed":
                rec.discount = rec.discount_amount
                rec.amount_total -= rec.discount_amount
                if rec.discount > rec.amount_untaxed:
                    raise UserError(_("Discount Must be less than total amount"))
            elif rec.discount_type == "percentage":
                total = (rec.amount_untaxed * rec.discount_amount) / 100
                rec.discount = total
                rec.amount_total -= total
                if rec.discount > rec.amount_untaxed:
                    raise UserError(_("Discount Must be less than amount"))
   
    # @api.depends("order_line.price_total", "discount_amount", "discount_type")
    # def _amount_all(self):
    #     res = super(sale_order, self)._amount_all()
    #     for rec in self:
    #         if rec.discount_amount < 0:
    #             raise UserError(
    #                 _(
    #                     "Discount Amount Must be zero OR grater than zero OR positive amount"
    #                 )
    #             )
    #         elif rec.discount_type == "fixed":
    #             rec.amount_total = rec.amount_untaxed - rec.discount
    #             if rec.discount > rec.amount_untaxed:
    #                 raise UserError(_("Discount Must be less than total amount"))
    #         elif rec.discount_type == "percentage":
    #             total = (rec.amount_untaxed * rec.discount_amount) / 100
    #             rec.amount_total = rec.amount_untaxed - total
    #             if rec.discount > rec.amount_untaxed:
    #                 raise UserError(_("Discount Must be less than total amount"))
    #     return res

    def _prepare_invoice(self):
        res = super(sale_order, self)._prepare_invoice()
        if self.discount_amount < 0:
            raise UserError(
                _("Discount Amount Must be zero OR grater than zero OR positive amount")
            )
        elif self.discount_type == "fixed":
            res.update(
                {
                    "discount_amount": self.discount_amount,
                    "discount_type": self.discount_type,
                    "discount": self.discount,
                }
            )
        elif self.discount_type == "percentage":
            res.update(
                {
                    "discount_amount": self.discount_amount,
                    "discount_type": self.discount_type,
                    "discount": self.discount,
                }
            )
        return res
