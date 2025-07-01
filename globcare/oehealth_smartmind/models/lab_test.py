from odoo import models, fields, api


class OeHealthLabTests(models.Model):
    _inherit = 'oeh.medical.lab.resultcriteria'

    result_status = fields.Selection([('normal', 'Normal'), ('be_careful', 'Be careful'), ('abnormal', 'Abnormal')],
                                     string='Result Status')

    def check_result_status(self,result_val,nrml_range,opr):

        # For string
        if opr == 'string':
            if result_val == nrml_range:
                return 'normal'
            else:
                return 'abnormal'

        range_split = nrml_range.split(str(opr))
        minimum_value = range_split[0] and float(range_split[0]) or False
        max_value = float(range_split[1])

        # For greater than
        if opr == '>':
            result = max_value
            total = 0.1 * result
            if result_val >= (max_value):
                return 'normal'
            else:
                if result_val > (max_value + total):
                    return 'abnormal'
                else:
                    return 'be_careful'

        # For Range, Upto, lessthan, String
        if minimum_value:
            result = max_value - minimum_value
            total = 0.1 * result
            if result_val >= (minimum_value) and result_val <= (max_value):
                return 'normal'
            else:
                if result_val < (minimum_value - total) or result_val > (max_value + total):
                    return 'abnormal'
                else:
                    return 'be_careful'
        else:
            result = max_value
            total = 0.1 * result
            if result_val <= (max_value - total):
                return 'normal'
            else:
                if result_val > (max_value + total):
                    return 'abnormal'
                else:
                    return 'be_careful'

    @api.onchange('result')
    def onchange_result_id(self):
        if self.result and self.normal_range:
            # result_val = float(self.result)
            nrml_range = self.normal_range
            if "-" in nrml_range:
                self.result_status = self.check_result_status(float(self.result), nrml_range, '-')
            elif "<" in nrml_range:
                self.result_status = self.check_result_status(float(self.result), nrml_range, '<')
            elif ">" in self.normal_range:
                self.result_status = self.check_result_status(float(self.result), nrml_range, '>')
            elif "Upto" in self.normal_range:
                self.result_status = self.check_result_status(float(self.result), nrml_range, 'Upto')
            elif self.normal_range:
                self.result_status = self.check_result_status(self.result, nrml_range, 'string')
        else:
            if self.result == "":
                self.result_status = False


class OeHealthLabTests(models.Model):
    _inherit = 'oeh.medical.lab.test'

    result_status = fields.Selection([('normal', 'Normal'), ('be_careful', 'Be careful'), ('abnormal', 'Abnormal')],
                                     string='Result Status')
    result = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string="Result", compute='_compute_result',store=True)

    @api.depends('lab_test_criteria.result_status')
    def _compute_result(self):
        for rec in self:
            if len(rec.lab_test_criteria) > 0:
                if any(rec.result_status == 'abnormal' or rec.result_status == 'be_careful' for rec in rec.lab_test_criteria):
                    # rec.write({'result' : "abnormal"})
                    rec.result = "abnormal"
                    # return "abnormal"
                else:
                    if any(rec.result_status == 'normal' for rec in rec.lab_test_criteria):
                        # rec.write({'result':"normal"})
                        rec.result = "normal"
                        # return "normal"
                    elif all(rec.result_status == 'normal' for rec in rec.lab_test_criteria):
                        rec.write({'result':"normal"})
                        return "normal"
                    else:
                        rec.write({'result': False})
                        # return False
            else:
                rec.write({'result':False})
                # return False

class OeHealthLabTestTypes(models.Model):
    _inherit = 'oeh.medical.labtest.criteria'

    range_type = fields.Selection([
        ('string','String'),
        ('range','Range'),
        ('upto','Upto'),
        ('<','<'),
        ('>','>'),
    ],string="Range Type")
    min_value = fields.Float("Minimum Value")
    max_value = fields.Float("Maximum Value")
    str_range_value = fields.Char("Value")

    @api.onchange('rang_type','max_value','min_value','str_range_value')
    def onchange_rang_type_id(self):
        print("onchange")
        if self.range_type == 'string':
            self.normal_range = self.str_range_value
        elif self.range_type == 'range':
            self.normal_range = str(self.min_value) + " - " + str(self.max_value)
        elif self.range_type == 'upto':
            self.normal_range = "Upto " + str(self.max_value)
        elif self.range_type == '<':
            self.normal_range = "< " + str(self.max_value)
        elif self.range_type == '>':
            self.normal_range = "> " + str(self.max_value)

class OeHealthLabTestTypes(models.Model):
    _inherit = 'oeh.medical.labtest.types'

    range_type = fields.Selection([
        ('string','String'),
        ('range', 'range'),
        ('upto', 'Upto'),
        ('<', '<'),
        ('>', '>'),
    ])
    min_value = fields.Float("Minimum Value")
    max_value = fields.Float("Maximum Value")
    str_range_value = fields.Char("Value")

