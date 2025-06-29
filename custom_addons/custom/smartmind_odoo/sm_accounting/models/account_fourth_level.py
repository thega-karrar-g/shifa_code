from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class AccountintFourthLevel(models.Model):

    _name = "sm.shifa.account.fourth.level"
    _rec_name = "account_4level"
    _order = 'code_prefix_start'

    account_4level = fields.Char(string="Fourth Level", required=True, translate=True)
    # parent_id = fields.Many2one('account.group', index=True, ondelete='cascade', readonly=True)
    third_level = fields.Many2one('account.group', index=True, string="Third Level", ondelete='cascade', required=True)
    fourth_level_number = fields.Char(string="number", required=True)
    code_prefix_start = fields.Char()
    code_prefix_end = fields.Char()

    @api.constrains('fourth_level_number')
    def _constraint_number_overlap(self):
        self.env['sm.shifa.account.fourth.level'].flush()
        query = """
                SELECT other.fourth_level_number FROM sm_shifa_account_fourth_level this
                JOIN sm_shifa_account_fourth_level other
                  ON other.fourth_level_number = this.fourth_level_number
                 AND other.id != this.id
                WHERE this.id IN %(ids)s
            """
        self.env.cr.execute(query, {'ids': tuple(self.ids)})
        res = self.env.cr.fetchall()
        if res:
            raise ValidationError(_('Account level four with the same number can\'t overlap'))

    #  fill start and end code
    @api.onchange("third_level", "fourth_level_number")
    def get_3nd_level_number(self):
        if self.third_level and self.fourth_level_number:
            length = self.fourth_level_number
            if len(str(length)) == 2:
                pass
            elif len(str(length)) > 2 or len(str(length)) < 2:
                raise ValidationError("Please Enter a digit between 01 and 99")
            #   set a value for start and end code
            if self.third_level.second_level.first_level_number:
                self.code_prefix_start = str(self.third_level.second_level.first_level_number) + str(self.third_level.second_level.second_level_number) + str(self.third_level.third_level_number) + str(self.fourth_level_number) +"000"
                self.code_prefix_end = str(self.third_level.second_level.first_level_number) + str(self.third_level.second_level.second_level_number) + str(self.third_level.third_level_number) + str(self.fourth_level_number) + "999"
            elif str(self.second_level.first_level_number) == "False":
                raise ValidationError("Please Enter a number for Second Level")




