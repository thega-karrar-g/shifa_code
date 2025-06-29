from odoo import models, fields, api

class SmPatientMedicinesFrequencies(models.Model):
    _name = 'sm.medicines.frequencies'
    _description = "Patient Medicines Frequencies"

    NUMBER_TIMES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ]

    name = fields.Char(string="Frequency")
    number_of_times = fields.Selection(NUMBER_TIMES, 'Number of times a day', index=True)
    is_missed = fields.Boolean(string="Missed Time")
