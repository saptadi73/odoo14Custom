# -*- coding: utf-8 -*-
import json
import logging
import functools
import werkzeug.wrappers

from odoo import http, models
from odoo.addons.asa_api.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = request.env["api.access_token"].sudo().search([("token", "=", access_token)],
                                                                          order="id DESC", limit=1)

        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(Http, self).session_info()
        user = request.env.user
        result['tipe_user']= user.tipe_user

        return result


class AsaApi(http.Controller):

    @http.route("/api/login", methods=["POST"], type="http", auth="none", csrf=False)
    def api_login(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           eq = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))

        If you would like to use body to send the data you can do the following:
            payload = request.httprequest.data.decode()
            payload = json.loads(payload)
            db, username, password = (
                payload.get("db"),
                payload.get("login"),
                payload.get("password"),
            )
        """
        params = ["db", "login", "password"]
        print ("===============test==============")
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing error", "either of the following are missing [db, username,password]", 403,
                )
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = request.env["api.access_token"].find_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    "user_context": request.session.get_context() if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "company_ids": request.env.user.company_ids.ids if uid else None,
                    "partner_id": request.env.user.partner_id.id,
                    "access_token": access_token,
                    "company_name": request.env.user.company_name,
                    "country": request.env.user.country_id.name,
                    "contact_address": request.env.user.contact_address,
                }
            ),
        )

    @http.route("/api/login/token_api_key", methods=["GET"], type="http", auth="none", csrf=False)
    def api_login_api_key(self, **post):
        # The request post body is empty the credetials maybe passed via the headers.
        headers = request.httprequest.headers
        db = headers.get("db")
        api_key = headers.get("api_key")
        _credentials_includes_in_headers = all([db, api_key])
        if not _credentials_includes_in_headers:
            # Empty 'db' or 'username' or 'api_key:
            return invalid_response(
                "missing error", "either of the following are missing [db ,api_key]", 403,
            )
        # Login in odoo database:
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        # request.session.authenticate(db, username, api_key)
        if not user_id:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        uid = user_id
        user_obj = request.env['res.users'].sudo().browse(int(uid))

        # Generate tokens
        access_token = request.env["api.access_token"].find_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    "company_id": user_obj.company_id.id if uid else None,
                    "company_ids": user_obj.company_ids.ids if uid else None,
                    "partner_id": user_obj.partner_id.id,
                    "access_token": access_token,
                    "company_name": user_obj.company_name,
                    "country": user_obj.country_id.name,
                    "contact_address": user_obj.contact_address,
                }
            ),
        )

    # @validate_token
    # @http.route('/change_password', auth="none", type='json', csrf=False)
    # def change_password(self, **rec):
    #     result = {}
    #     if request.jsonrequest :
    #         if rec.get('new_password') and rec.get('user_id'):
    #             user = request.env['res.users'].sudo().search([('id','=',rec.get('user_id'))])
    #             user.sudo().write({'password': rec['new_password']})
    #             return ({'result':'success'})
    #         return ({'result':'User Or Password is Empty'})
    #     return ({'result':'Failed Check Your Parameter'})

    # @validate_token
    # @http.route('/change_password_with_token', methods=["POST"], type="http", auth="none", csrf=False)
    # def change_password(self, **post):
    #     try:
    #         user_id = request.uid
    #         user_obj = request.env['res.users'].browse(user_id)
    #         user_id         = post.get("user_id")
    #         new_password    = post.get("new_password")

    #         res_user_obj = request.env['res.users']
    #         updated_password = res_user_obj.browse(int(user_id))
    #         is_updated = updated_password.with_user(user_obj).write({
    #                                                                 'password': new_password
    #                                                                 })
    #         if is_updated:
    #             return valid_response([{"user_id": user_id, "message": "Password updated successfully"}], status=200)
    #     except Exception as e:
    #         return {'status': False, 'error': str(e)}


    #@validate_token
    @http.route('/change_password', auth="none", type='json',cors='*')
    def change_password(self, **rec):
        try:
            header = request.httprequest.headers
            db= header.get('db')
            login = header.get('login')
            password = header.get('password')
            uid = request.session.authenticate(db, login, password)
            if uid:
                if rec.get('new_password') and rec.get('user_id'):
                    user = request.env['res.users'].sudo().search([('id','=',rec.get('user_id'))])
                    user.write({'password': rec['new_password']})
                    return ({'result':'success'})
                return ({'result':'User Or Password is Empty'})
                
        except Exception as e:
            return {'status': False, 'error': str(e)}