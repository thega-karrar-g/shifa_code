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

from odoo import http
from odoo.http import request
from O365 import Account, FileSystemTokenBackend
import werkzeug
import os
import subprocess
import json


class AcsVideoCall(http.Controller):

    @http.route(['/videocall/<string:meeting_name>'], type='http', auth="public", website=True)
    def acs_videocall(self, meeting_name, **kw):
        print("========================49================", meeting_name)
        videocall_server_url = request.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        print("================50==================== tele soources", videocall_server_url)
        site_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print("=============25 site url===:", site_url)
        values = {
            'meeting_name': meeting_name,
            'server_name': videocall_server_url.split("//")[1],
            'site_url': site_url,
            # 'meeting': meeting,
        }
        # else:
        #     raise ValueError("Please First Write Server URL")
        # print("33:::::::::::::::::::::::::::::", values)
        return request.render("oehealth_jitsi.acs_videocall", values)
