# -*- coding: utf-8 -*-
import logging
import jwt

from openid.cryptutil import randomString
from .. import utils

from odoo import fields
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import *

from openerp import SUPERUSER_ID
from odoo.modules.registry import Registry
from openerp.addons.web.controllers.main import login_and_redirect, set_cookie_and_redirect
import openerp.http as http
from odoo.addons.tko_web_sessions_management.models.main import HomeTkobr
from openerp.http import request, Response

_logger = logging.getLogger(__name__)


class ALJwtAuthentication(HomeTkobr, http.Controller):
    @http.route('/jwt/login/<string:jwtoken>', type='http', auth="none")
    def jwt_authenticate(self, **kwargs):

        values = dict(kwargs)

        redirect = '/web?'
        now = fields.datetime.now()

        with request.registry.cursor() as cr:
            dbname = cr.dbname
            registry = request.registry.get(dbname)
            agencies_obj = request.registry.get('al.agency')
            users_obj = request.env['res.users']
            # Get session
            sessions_obj = request.env['ir.sessions']
            # JWT Header
            header = jwt.get_unverified_header(values['jwtoken'])
            print("Header : ", header)

            # Get IP, check if it's behind a proxy
            ip = request.httprequest.headers.environ['REMOTE_ADDR']
            if 'HTTP_X_FORWARDED_FOR' in request.httprequest.headers.environ and \
                    request.httprequest.headers.environ[
                        'HTTP_X_FORWARDED_FOR']:
                forwarded_for = request.httprequest.headers.environ['HTTP_X_FORWARDED_FOR'].split(', ')
                if forwarded_for and forwarded_for[0]:
                    ip = forwarded_for[0]

            # Security check levels
            if 'ip' in header:
                print(ip)
                print(type(ip))
                ip_jwt = header['ip']
                if ip_jwt != ip:
                    return Response(u"Adresse IP non autorisée  !", status=400)
            if 'exp' in header:
                expiration_date = datetime.fromtimestamp(int(header['exp']))
                print("expiration Date", expiration_date)
                print("Date now", now)
                if expiration_date <= now:
                    return Response(u"Token expiré  !", status=400)

            try:
                # Payload
                JWT_SECRECT = request.env['ir.config_parameter'].sudo().get_param('jwt.secret_key')
                JWT_ALGORITHM = request.env['ir.config_parameter'].sudo().get_param('jwt.algorithm')
                payload = jwt.decode(values['jwtoken'], JWT_SECRECT, algorithms=[JWT_ALGORITHM])
                print("Payload : ", payload)
            except Exception as e:
                return Response(e, status=400)

            # Search for Correct User
            user_ids = False
            #Process token from MS
            if set(('user_type','user_identifier')) <= set(payload):
                if payload['user_type'] == 'PR':
                    user_ids = users_obj.search([('user_cin', '=', payload['user_identifier'])])
                elif payload['user_type'] == 'FR':
                    cc_group_id = request.registry.get('ir.model.data').get_object_reference('mobilab_agency', 'group_agencies_cc')[1]
                    cc_senior_group_id = request.registry.get('ir.model.data').get_object_reference('mobilab_agency', 'group_agencies_cc_senior')[1]
                    agency_id = agencies_obj.search([('agency_code', '=', payload['user_identifier'])])
                    if agency_id:
                        user_ids = users_obj.search([
                            ('agency_ids', '=', agency_id),
                            ('groups_id', '=', cc_group_id),
                            ('groups_id', '!=', cc_senior_group_id),
                        ])
                else:
                    return Response(u"Code erreur [TUinP].", status=400)
            
            #Process token from Odoo 8
            if set(('issuer','user_identifier')) <= set(payload):
                if payload['issuer'] == 'Openerp 8.0-20170815':
                    user_ids = users_obj.search([('login', '=', payload['user_identifier'])])
                else:
                    return Response(u"Unauthorized issuer", status=400)

            if user_ids and len(user_ids) == 1:
                sid = request.httprequest.session.sid
                user_id = user_ids[0]
                user = users_obj.browse(user_id)
                company_id = user_id.company_id.id
                key = randomString(utils.KEY_LENGTH, '0123456789abcdef')
                user_id.sudo().write({'jwt_key': key})
                # Session
                sessions_ids = sessions_obj.search([
                    # ('session_id', '=', sid),
                    # ('ip', '=', ip),
                    ('user_id', '=', user_id.id),
                    ('logged_in', '=', True)
                ])
                print("sessions_ids : ", sessions_ids)
                if sessions_ids:
                    sessions = sessions_obj.browse(sessions_ids)
                    for session in sessions_ids:
                        session.action_close_session()
                
                sess = {
                    'user_id': user_id.id,
                    'logged_in': True,
                    'session_id': sid,
                    'session_seconds': user_id.with_context(force_company=company_id).session_default_seconds,
                    'multiple_sessions_block': user.with_context(force_company=company_id).multiple_sessions_block,
                    'date_login': now,
                    'date_expiration': datetime.strftime(
                        (datetime.strptime(str(now).split(".")[0], DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(
                            seconds=user_id.with_context(force_company=company_id).session_default_seconds)),DEFAULT_SERVER_DATETIME_FORMAT),
                    'ip': ip,
                    # 'ip_location': ip_location,
                    'remote_tz': 'GMT',
                }
                sessions_obj.create(sess)
                request.env.cr.commit()
                return login_and_redirect(db=dbname, login=user_id.login, key=key, redirect_url=redirect)
            else:
                return Response(u"Aucun utilisateur trouvé !", status=400)
        return Response(u"Erreur de connexion !", status=400)

