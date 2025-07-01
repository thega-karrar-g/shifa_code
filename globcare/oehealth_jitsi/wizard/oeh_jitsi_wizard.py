##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################
import uuid

from odoo import api, fields, models, _


class OehJitsiMeeting(models.TransientModel):
    _name = "jitsi.meeting"
    _description = "jitsi Meeting"

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    jitsi_meeting_url = fields.Char("URL For Jitsi Meeting")
    meeting_link = fields.Char(string='Meeting Link', default='')
    meeting_code = fields.Char(string='Meeting Code', default=_get_meeting_code)

    def create_meeting(self):
        server_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/videocall'
        print("=======================56 server url  =======================", server_url)

        appointment = self.env['oeh.medical.appointment'].browse(self.env.context.get('active_id'))
        print("===43===")
        # if self.sources_name == 'jitsi':
        meeting_link = server_url + '/' + self.meeting_code
        print("===============64======================meeting link::::::::::::", meeting_link)
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link
        # print("====71====",invitation_text)
        # meeting_link = invitation_text + '/' + self.meeting_code

        print("====+=====+===+=45===== dfd==dsd==dsd==sds==sdsd==sd=s=")
        appointment.write({
            'invitation_text_jitsi': meeting_link
        })
        print("::::::::::::::::::;;;51;;;", self.meeting_link)
