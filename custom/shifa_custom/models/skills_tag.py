from odoo import api, fields, models
from odoo.exceptions import UserError

class SkillsTag(models.Model):
    _name = 'skills.tag'
    _description = 'Skill Tag'

    name = fields.Char(string='Skill', required=True)


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Skill must be unique.'),
    ]
