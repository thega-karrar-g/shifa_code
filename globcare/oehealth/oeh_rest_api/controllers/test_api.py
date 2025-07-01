from odoo import http
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods


class SmartMindTestRESTAPIController(http.Controller, SmartMindSharedMethods):

    def __init__(self):
        self._model = 'ir.model'
