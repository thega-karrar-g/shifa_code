from odoo import models, fields
from odoo.http import request


class ShifaPhysicianUpperActions(models.Model):
    _inherit = "oeh.medical.physician"

    def _instant_consultation_count(self):
        oe_apps = self.env['sm.shifa.instant.consultation']
        for pa in self:
            domain = [('doctor', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.instant_consultation_count = app_count
        return True

    def _count_compeleted_consultation(self):
        consult_obj = self.env['sm.shifa.instant.consultation']
        domain = [('state', '=', 'completed')]
        consult_ids = consult_obj.search(domain)
        # print(consult_ids)
        count = 0
        for rec in self:
            for i in consult_ids:
                if rec.name == i.doctor.name:
                    count = count+1
                    # print("this is count>>>>>>>>>",count)
            rec.completed_consult = count

    def _get_instant_charge(self):
        icc = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([('code', '=', 'ICC')], limit=1)
        self.commission_per_consult = icc.charge

    def _compute_total_commission(self):
        for rec in self:
            if rec.completed_consult > 0 and rec.commission_per_consult >= 0:
                rec.total_commission = (rec.completed_consult * rec.commission_per_consult)
            else:
                rec.total_commission = 0

    def _get_total_paid_amount(self):
        for rec in self:
            if rec.paid_amount_id:
                count_total = 0
                for i in rec.paid_amount_id:
                    count_total += i.amount
                #     print(i.amount)
                # print(count_total)
                rec.total_paid_amount = count_total
            else:
                rec.total_paid_amount = 0

    def _get_totals_penalties(self):
        for rec in self:
            if rec.penalties_id:
                count_total = 0
                for y in rec.penalties_id:
                    count_total += y.amount
                rec.total_penalties = count_total
            else:
                rec.total_penalties = 0

    def _get_commission_payable(self):
        for rec in self:
            if rec.total_paid_amount > 0 and rec.total_penalties > 0 and rec.total_commission > 0:
                rec.commission_payable = (rec.total_commission - rec.total_paid_amount - rec.total_penalties)
            else:
                rec.commission_payable = 0

    instant_consultation_count = fields.Integer(compute=_instant_consultation_count, string="Instant Consultation")
    completed_consult = fields.Integer(compute=_count_compeleted_consultation)
    commission_per_consult = fields.Integer(compute=_get_instant_charge)#inverse='_get_instant_charge'
    total_commission = fields.Integer(compute=_compute_total_commission)
    total_paid_amount = fields.Float(compute=_get_total_paid_amount)#
    total_penalties = fields.Float(compute=_get_totals_penalties)#
    commission_payable = fields.Float(compute=_get_commission_payable)


    paid_amount_id = fields.One2many('sm.shifa.paid.amount', 'paid_amount_ref_id', string='Paid Amount')
    penalties_id = fields.One2many('sm.shifa.penalties', 'penalties_ref_id', string='Penalties')


class ShifaPaidAmountInherit(models.Model):
    _inherit = 'sm.shifa.paid.amount'

    paid_amount_ref_id = fields.Many2one('oeh.medical.physician', string='Paid Amount', ondelete='cascade', domain=[('active', '=', True)],)


class ShifaPenalties(models.Model):
    _inherit = 'sm.shifa.penalties'

    penalties_ref_id = fields.Many2one('oeh.medical.physician', string='Penalties', ondelete='cascade', domain=[('active', '=', True)],)
