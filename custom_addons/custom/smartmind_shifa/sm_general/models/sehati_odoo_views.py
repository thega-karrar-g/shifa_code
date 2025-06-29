from odoo import api, fields, models, tools


class HrEmployeeShifa(models.Model):
    _inherit = "hr.employee"

    def _physician_count(self):
        physician_obj = self.env['oeh.medical.physician']
        for emp in self:
            domain = [('employee_id', '=', emp.id)]
            physician_ids = physician_obj.search(domain)
            physician = physician_obj.browse(physician_ids)
            count = 0
            for phy in physician:
                count += 1
            emp.phy_count = count
            return True

    def open_physician_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('oehealth.oeh_medical_physician_action_tree')
        action['domain'] = [('employee_id', '=', self.id)]
        return action

    job_title_person = fields.Many2one('hr.job')
    phy_count = fields.Integer(compute=_physician_count, string="Medical Staff")

