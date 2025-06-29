from odoo import models, api

class CustomCallcenter(models.Model):
    _inherit = "sm.shifa.call.center.census"

    def test_print(self):
        print('-------------------------------------------------------')
        
