
from odoo import api, fields, models


class SMLabTestDepartment(models.Model):
    _inherit = 'oeh.medical.labtest.department'

    # archive feature #
    active = fields.Boolean('Archive', default=True)


class SMLabTestType(models.Model):
    _inherit = 'oeh.medical.labtest.types'

    # archive feature #
    active = fields.Boolean('Archive', default=True)


