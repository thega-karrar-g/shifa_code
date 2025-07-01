
import json
import base64
import logging
import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools import html_escape
from odoo.addons.web.controllers.main import _serialize_exception


class SmartmindOdooController(http.Controller):

    @http.route('/web/attachments/token/<string:token>', type='http', auth="none")
    def get_attachments(self, token, **kwargs):
        try:
            attachment_ids = request.env['ir.attachment'].sudo().search([('access_token', '=', token)])
            if attachment_ids:
                # print(attachment_ids)
                for attachment_obj in attachment_ids:
                    filecontent = base64.b64decode(attachment_obj.datas)
                    # disposition = 'attachment; filename=%s' % werkzeug.urls.url_quote(attachment_obj.datas_fname)
                    # print(disposition)
                    return request.make_response(
                        filecontent,
                        [('Content-Type', attachment_obj.mimetype),
                         ('Content-Length', len(filecontent)),
                         ('Content-Disposition', False)])
            else:
                error = {
                    'code': 200,
                    'message': "Unable to find the attachments",
                }
            return request.make_response(html_escape(json.dumps(error)))

        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                # 'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4: