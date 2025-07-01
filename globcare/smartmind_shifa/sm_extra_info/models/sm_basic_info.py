from odoo import models, fields, api


class ShifaJobs(models.Model):
    _name = "sm.shifa.job"
    _description = "Medical Staff Jobs"

    name = fields.Char(string='Job Title', size=128, required=True)
    name_ar = fields.Char(string='Job Title (AR)', size=128)

    _order = 'name'
    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The Job name must be unique')]


class ShifaJobsLicense(models.Model):
    _name = "sm.shifa.jobs.license"
    _description = "Medical Staff Jobs Licenses"

    job = fields.Many2one('sm.shifa.job', string='Job Title', required=True)
    name = fields.Char(string='Job Classification', required=True)
    name_ar = fields.Char(string='Job Classification (AR)')

    _order = 'name'
    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The License name must be unique')]


class ShifaLanguages(models.Model):
    _name = "sm.shifa.language"
    _description = "Doctor Spoken Languages"

    name = fields.Char(string='Name', required=True)
    name_ar = fields.Char(string='Name (AR)')


# class ShifaEmployer(models.Model):
#     _name = "sm.shifa.employer"
#     _description = "Medical Staff Employer"
#
#     name = fields.Char(string='Employer Name', size=128, required=True)
#     name_ar = fields.Char(string='Employer Name (AR)', size=128)
#
#     _order = 'name'
#     _sql_constraints = [
#         ('code_uniq', 'unique (name)', 'The Employer name must be unique')]

# access_sm_shifa_jobs_employer,sm.shifa.employer,model_sm_shifa_employer,,1,1,1,1