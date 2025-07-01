from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ShifaAccountThirdLevel(models.Model):
    _inherit = "account.group"
    _rec_name = "second_level"

    second_level = fields.Many2one('account.account.type', index=True, ondelete='cascade',  required=True)
    # test account
    # third_level_number = fields.Char(string="number", required=True)

    # @api.onchange("second_level", "third_level_number")
    # def get_3nd_level_number(self):
    #     if self.second_level and self.third_level_number:
    #         length = self.third_level_number
    #         if len(str(length)) == 2:
    #             pass
    #         elif len(str(length)) > 2 or len(str(length)) < 2:
    #             raise ValidationError("Please Enter a digit between 01 and 99")
    #     #   set a value for start and end code
    #         if self.second_level.first_level_number:
    #             self.code_prefix_start = str(self.second_level.first_level_number) + str(self.second_level.second_level_number) + str(self.third_level_number) + "0000"
    #             self.code_prefix_end = str(self.second_level.first_level_number) + str(self.second_level.second_level_number) + str(self.third_level_number) + "9999"
    #         elif str(self.second_level.first_level_number) == "False":
    #             raise ValidationError("Please Enter a number for Second Level")
