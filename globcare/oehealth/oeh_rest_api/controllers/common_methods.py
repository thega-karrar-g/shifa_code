import ast
import json
import werkzeug.wrappers
from odoo.http import request
import base64
import pytz
from datetime import datetime
import xmlrpc.client
from odoo import http


def authenticate_user(username, password):
    db = request.env.cr.dbname
    # base_url = request.httprequest.host_url
    wsgienv = request.httprequest.environ
    REMOTE_ADDR = wsgienv['REMOTE_ADDR']
    # base_url = 'http://{}:8069/'.format(REMOTE_ADDR)
    base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(base_url))
    uid = common.authenticate(db, username, password, {})
    return uid


def valid_response(data, status=200):
    """
    Access-Control-Allow-Credentials: true
    This method will return VALID RESPONSE when the API request was successfully processed."""
    data_to_post = {
        'success': 1,
        'data': data
    }
    return werkzeug.wrappers.Response(
        status=status,
        headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': True},
        content_type='application/json; charset=utf-8',
        response=json.dumps(data_to_post),
    )


def invalid_response(typ, message=None, status=200):
    """This method will return INVALID RESPONSE value whenever the server runs into an error
    either from the client or the server."""
    return werkzeug.wrappers.Response(
        status=status,
        headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': True},
        content_type='application/json; charset=utf-8',
        response=json.dumps({
            'success': 0,
            'message': str(message) if message else 'wrong arguments (missing validation)',
        }),
    )


def extract_arguments(payload, offset=0, limit=0, order=None):
    """This method will extract arguments for searching records """
    fields, domain = [], []
    if payload.get('domain'):
        domain += ast.literal_eval(payload.get('domain'))
    if payload.get('fields'):
        fields += ast.literal_eval(payload.get('fields'))
    if payload.get('offset'):
        offset = int(payload['offset'])
    if payload.get('limit'):
        limit = int(payload['limit'])
    if payload.get('order'):
        order = payload.get('order')
    return [domain, fields, offset, limit, order]


def get_file_name(file, file_name):
    if file:
        files = request.httprequest.files.getlist(file_name)
        for ufile in files:
            return ufile.filename


def upload_attached_file(file, file_name):
    if file:
        files = request.httprequest.files.getlist(file_name)
        for ufile in files:
            try:
                file_data = base64.encodebytes(ufile.read())
                # file_data = base64.encodestring(ufile.read())
                file_data_to_send = file_data.decode('utf-8')
                return file_data_to_send
            except Exception as e:
                return invalid_response('failed to upload file', e)


def convert_date_to_utc(date):
    local = pytz.timezone('Asia/Riyadh')
    naive = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def convert_utc_to_local(date):
    date_format = "%Y-%m-%d %H:%M:%S"
    user_tz = request.env.user.tz or 'Asia/Riyadh'
    local = pytz.timezone(user_tz)
    local_date = datetime.strftime(pytz.utc.localize(datetime.strptime(date, date_format)).astimezone(local),
                                   date_format)
    return local_date
