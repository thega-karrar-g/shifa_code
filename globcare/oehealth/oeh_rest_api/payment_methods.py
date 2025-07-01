from odoo.http import request
from datetime import datetime


class SmartMindPaymentMethods:

    def create_purchase_order(self, ins_cons):
        model_name = "purchase.order"
        count = request.env[model_name].sudo().search_count([('instant_consultation', '=', int(ins_cons.id))])
        if count <= 0:
            purchase_order = request.env[model_name].sudo().create({
                'partner_id': ins_cons.doctor.oeh_user_id.partner_id.id,
                'instant_consultation': ins_cons.id,
                'state': 'purchase',
            })

            self.create_purchase_order_line(ins_cons.miscellaneous_charge.name,
                                            ins_cons.miscellaneous_charge.product_id.id,
                                            ins_cons.miscellaneous_charge.standard_price, purchase_order.id)
            return purchase_order.id

    def create_purchase_order_line(self, name, product_id, price, order_id):
        request.env['purchase.order.line'].create({
            'name': name,
            'product_id': product_id,
            'product_qty': 1,
            'price_unit': price,
            'order_id': order_id,
            'taxes_id': False,
        })

    def create_sale_order(self, ins_cons):
        model_name = "sale.order"
        count = request.env[model_name].sudo().search_count([('instant_consultation', '=', int(ins_cons.id))])
        if count <= 0:
            if ins_cons.insurance:
                partner_val = ins_cons.insurance.partner_id.id
            else:
                partner_val = ins_cons.patient.partner_id.id

            sale_order = request.env[model_name].sudo().create({
                'partner_id': partner_val,
                'client_order_ref': "Instant Consultation : " + ins_cons.name,
                'instant_consultation': ins_cons.id,
                'state': 'sale',
            })

            self.create_sale_order_line(ins_cons.miscellaneous_charge.name,
                                        ins_cons.miscellaneous_charge.product_id.id,
                                        ins_cons.miscellaneous_charge.list_price,
                                        ins_cons.discount_percent,
                                        ins_cons.ksa_nationality, sale_order.id)
            return sale_order.id

    def create_sale_order_line(self, name, product_id, price, discount, ksa, order_id):
        sale_order_line = request.env['sale.order.line'].create({
            'name': name,
            'product_id': product_id,
            'product_uom_qty': 1,
            'price_unit': price,
            'discount': discount,
            'order_id': order_id,
        })
        if ksa == 'NON':
            sale_order_line.product_id_change()

    def create_requested_payment(self, ins_cons):
        model_name = 'sm.shifa.requested.payments'
        count = request.env[model_name].sudo().search_count([('instant_consultation', '=', int(ins_cons.id))])
        if count <= 0:
            rp = request.env[model_name].sudo().create({
                'patient': int(ins_cons.patient),
                'date': datetime.now().date(),
                'instant_consultation': ins_cons.id,
                'payment_amount': ins_cons.amount_payable,
                'deduction_amount': ins_cons.deduction_amount,
                'payment_reference': ins_cons.payment_reference,
                'details': ins_cons.name,
                'payment_method': 'mobile',
                'state': 'Paid',
            })
            rp.sudo().create_account_payment()
            return rp.id
