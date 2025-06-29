
import logging
from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)


class SmPatient(models.TransientModel):
    _name = 'sm.patient.search'
    name = fields.Char('Search', help="If you want to search for multiple values, please put a comma between them!")
    patient_ids = fields.Many2many('oeh.medical.patient',string='Patients',compute="_compute_patients",store=True)

    @api.depends('name')
    def _compute_patients(self):
        for record in self:
            record['patient_ids'] = [(5, 0, 0)]
            if record.name:
                values = record.name.split(',')
                for value in values:
                    patients = self.env['oeh.medical.patient'].sudo().search([
                        '|', '|', 
                        ('ssn', 'ilike', value), 
                        ('name', 'ilike', value),
                        ('mobile', 'ilike', value)])
                    if patients:
                        for patient in patients:
                            record['patient_ids'] = [(4, patient.id)]
