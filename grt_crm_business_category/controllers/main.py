from odoo import fields, http
from odoo.http import request


class GrtCrmBusinessCategoryController(http.Controller):
    @http.route("/grt_crm_business_category/gps/ping", type="json", auth="user")
    def gps_ping(self, latitude=None, longitude=None, client_time=None, client_tz=None):
        if latitude is None or longitude is None:
            return {"ok": False}
        user = request.env.user.sudo()
        user.write(
            {
                "last_gps_latitude": latitude,
                "last_gps_longitude": longitude,
                "last_gps_client_time": client_time or False,
                "last_gps_client_tz": client_tz or False,
                "last_gps_recorded_at": fields.Datetime.now(),
            }
        )
        return {"ok": True}
