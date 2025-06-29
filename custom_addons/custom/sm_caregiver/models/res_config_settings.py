from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    caregiver_deferred_income_account_id = fields.Many2one('account.account')
    caregiver_credit_account_id = fields.Many2one('account.account')
    caregiver_journal_id = fields.Many2one('account.journal')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        res.update({
            'caregiver_deferred_income_account_id': int(IrConfigPrmtr.get_param('sm_caregiver.caregiver_deferred_income_account_id')),
            'caregiver_credit_account_id': int(IrConfigPrmtr.get_param('sm_caregiver.caregiver_credit_account_id')),
            'caregiver_journal_id' : int(IrConfigPrmtr.get_param('sm_caregiver.caregiver_journal_id')),
        })
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            "sm_caregiver.caregiver_deferred_income_account_id", self.caregiver_deferred_income_account_id.id,
        )
        IrConfigPrmtr.set_param(
            "sm_caregiver.caregiver_credit_account_id", self.caregiver_credit_account_id.id,
        )
        IrConfigPrmtr.set_param(
            "sm_caregiver.caregiver_journal_id", self.caregiver_journal_id.id,
        )

