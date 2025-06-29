from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ShifaAccountType(models.Model):
    _inherit = "account.account.type"

    FIRST_LEVEL = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Revenue'),
        ('expense', 'Expense'),
        ('off_balance', 'off_balance'),
    ]

    internal_group = fields.Selection(FIRST_LEVEL, string="Internal Group",
                                      required=True,
                                      help="The 'Internal Group' is used to filter accounts based on the internal group set on the account type.")
    active = fields.Boolean(default=True)
    # first_level_number = fields.Char()
    # second_level_number = fields.Char(string="number", required=True)
    # code_prefix_start = fields.Char()
    # code_prefix_end = fields.Char()

    # @api.onchange("internal_group")
    # def get_1st_level_number(self):
    #     if self.internal_group == "asset":
    #         self.first_level_number = "1"
    #     elif self.internal_group == "liability":
    #         self.first_level_number = "2"
    #     elif self.internal_group == "equity":
    #         self.first_level_number = "3"
    #     elif self.internal_group == "income":
    #         self.first_level_number = "4"
    #     elif self.internal_group == "expense":
    #         self.first_level_number = "5"
    #     elif self.internal_group == "off_balance":
    #         raise ValidationError("Choose a value for First Level")
    #
    # @api.constrains('code_prefix_start', 'code_prefix_end')
    # def _constraint_number_overlap(self):
    #     self.env['account.account.type'].flush()
    #     query = """
    #                 SELECT other.id FROM account_account_type this
    #                 JOIN account_account_type other
    #                   ON char_length(other.code_prefix_start) = char_length(this.code_prefix_start)
    #                  AND other.id != this.id
    #                  AND (
    #                     other.code_prefix_start <= this.code_prefix_start AND this.code_prefix_start <= other.code_prefix_end
    #                     OR
    #                     other.code_prefix_start >= this.code_prefix_start AND this.code_prefix_end >= other.code_prefix_start
    #                 )
    #                 WHERE this.id IN %(ids)s
    #             """
    #     self.env.cr.execute(query, {'ids': tuple(self.ids)})
    #     res = self.env.cr.fetchall()
    #     if res:
    #         raise ValidationError(_('Account second level with the same number can\'t overlap'))
    #
    # @api.onchange("second_level_number", "first_level_number")
    # def get_2nd_level_number(self):
    #     if self.second_level_number:
    #         length = self.second_level_number
    #         if len(str(length)) == 1:
    #             pass
    #         elif len(str(length)) > 1:
    #             raise ValidationError("Please Enter a digit between 1 and 9")
    #     #   set a value for start and end code
    #         self.code_prefix_start = str(self.first_level_number) + str(self.second_level_number) + "000000"
    #         self.code_prefix_end = str(self.first_level_number) + str(self.second_level_number) + "999999"