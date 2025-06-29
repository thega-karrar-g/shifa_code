from odoo import api, fields, models

class PhysicianAssessment(models.Model):
    _inherit = "sm.shifa.physician.assessment"
    _description = "Inherit from smart_more"
    _name = "sm.shifa.physician.assessment"  # Only if required for chatter to work
    _inherits = {}  # You do not need _inherits unless you're delegating fields

    # Enable chatter features
    _inherit = ["sm.shifa.physician.assessment", "mail.thread", "mail.activity.mixin"]

    clinical_notes = fields.Text(string="Clinical Notes")
    medical_care_plan = fields.Text(string='Medical Care Plan',readonly=False , tracking=True)
