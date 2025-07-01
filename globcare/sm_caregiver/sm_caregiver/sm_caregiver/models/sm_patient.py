from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from datetime import date


class Patient(models.Model):
    _inherit = "oeh.medical.patient"

    caregiver_contract_ids = fields.One2many('sm.caregiver.contracts','patient_requested_id')
    caregiver_contract_count = fields.Integer(compute="_compute_caregiver_count")
    multi_package_ids = fields.One2many('sm.shifa.package.appointments.multi','patient')
    multi_package_count = fields.Integer(compute="_compute_multi_package_count")

    def _compute_caregiver_count(self):
        for rec in self:
            rec.caregiver_contract_count = len(rec.caregiver_contract_ids)

    def _compute_multi_package_count(self):
        for rec in self:
            rec.multi_package_count = len(rec.caregiver_contract_ids)

    
    def action_view_caregiver_contracts(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sm_caregiver.sm_caregiver_contracts_action")
        action['domain'] = [('id', 'in', self.caregiver_contract_ids.ids)]
        return action
    
    def action_view_caregiver_multi_package(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("smartmind_shifa_more.sm_shifa_package_appointments_multi_action_tree")
        action['domain'] = [('id', 'in', self.multi_package_ids.ids)]
        return action
    
    def action_open_statement(self):
        lines = self.env['account.move.line'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('parent_state', '=', 'posted'),
            ('account_id.user_type_id', '=', 5)
        ])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_moves_all")
        action['domain'] = [('id', 'in', lines.ids)]
        action['context'] = {'search_default_group_by_partner': 1, 'create': 0}
        return action
    
    
class Partner(models.Model):
    _inherit = "res.partner"
    patient_ssn = fields.Char(compute="_compute_patient_id",string='ID Number')

    def _compute_patient_id(self):
        for record in self:
            patient = self.env['oeh.medical.patient'].sudo().search([
                ('partner_id','=',record.id)
            ],limit=1)
            record.patient_ssn = patient.ssn if patient else False

