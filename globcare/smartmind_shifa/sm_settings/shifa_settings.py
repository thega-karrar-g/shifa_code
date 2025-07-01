from odoo import api, fields, models


class ResConfigSettingsDuration(models.TransientModel):
    _inherit = 'res.config.settings'

    appointment_duration_hhc = fields.Float(string="HHC Default Duration", readonly=False, default=1.0)
    appointment_duration_pcr = fields.Float(string="PCR Default Duration", readonly=False, default=1.0)
    appointment_duration_phy = fields.Float(string="Physiotherapy Default Duration", readonly=False, default=1.0)

    @api.model
    def set_values(self):
        res = super(ResConfigSettingsDuration, self).set_values()
        self.env['ir.config_parameter'].set_param('smartmind_shifa.appointment_duration_hhc', self.appointment_duration_hhc)
        self.env['ir.config_parameter'].set_param('smartmind_shifa.appointment_duration_pcr', self.appointment_duration_pcr)
        self.env['ir.config_parameter'].set_param('smartmind_shifa.appointment_duration_phy', self.appointment_duration_phy)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsDuration, self).get_values()
        IC = self.env['ir.config_parameter'].sudo()
        hhc_duration = IC.get_param('smartmind_shifa.appointment_duration_hhc')
        pcr_duration = IC.get_param('smartmind_shifa.appointment_duration_pcr')
        phy_duration = IC.get_param('smartmind_shifa.appointment_duration_phy')
        res.update(
            appointment_duration_hhc=hhc_duration,
            appointment_duration_pcr=pcr_duration,
            appointment_duration_phy=phy_duration
        )
        return res
