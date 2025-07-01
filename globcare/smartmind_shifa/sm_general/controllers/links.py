from odoo import http
from odoo.http import request


class GlobCareLinks(http.Controller):

    @http.route(['/globcare/link'], auth="none")
    def show_link(self, **kw):
        return 'Hi, Mr. Mukhtar'
        # return request.render('smartmind_shifa.repo_temp', {})
