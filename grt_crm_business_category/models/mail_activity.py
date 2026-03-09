from odoo import _, api, fields, models
from datetime import timedelta


class MailActivity(models.Model):
    _inherit = "mail.activity"

    kilometer = fields.Float(string="Kilometer (KM)", digits=(16, 2))
    gps_captured = fields.Boolean(string="GPS Captured")
    gps_latitude = fields.Float(string="GPS Latitude", digits=(9, 6))
    gps_longitude = fields.Float(string="GPS Longitude", digits=(9, 6))
    gps_client_time = fields.Char(string="GPS Client Time")
    gps_client_tz = fields.Char(string="GPS Client TZ")
    gps_openstreetmap_url = fields.Char(string="OpenStreetMap URL")

    @staticmethod
    def _has_valid_gps(lat, lon):
        if lat is None or lon is None:
            return False
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (TypeError, ValueError):
            return False
        if abs(lat_f) < 1e-9 and abs(lon_f) < 1e-9:
            return False
        return -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0

    @staticmethod
    def _build_osm_url(lat, lon):
        return "https://www.openstreetmap.org/?mlat=%s&mlon=%s#map=18/%s/%s" % (lat, lon, lat, lon)

    @api.onchange("gps_latitude", "gps_longitude", "gps_captured")
    def _onchange_gps_openstreetmap_url(self):
        for activity in self:
            if activity._has_valid_gps(activity.gps_latitude, activity.gps_longitude):
                activity.gps_openstreetmap_url = activity._build_osm_url(activity.gps_latitude, activity.gps_longitude)
                activity.gps_captured = True
            else:
                activity.gps_openstreetmap_url = False

    @api.model_create_multi
    def create(self, vals_list):
        ctx = self.env.context
        ctx_gps_captured = bool(ctx.get("gps_captured"))
        ctx_lat = ctx.get("gps_latitude")
        ctx_lon = ctx.get("gps_longitude")
        ctx_client_time = ctx.get("gps_client_time")
        ctx_client_tz = ctx.get("gps_client_tz")

        for vals in vals_list:
            if vals.get("res_model") == "crm.lead" and not vals.get("user_id"):
                vals["user_id"] = self.env.user.id
            # Fallback: if popup payload keeps default zeros, use GPS from context.
            if ctx_gps_captured:
                current_lat = vals.get("gps_latitude")
                current_lon = vals.get("gps_longitude")
                if (not current_lat and current_lat != 0.0) or (not current_lon and current_lon != 0.0):
                    vals["gps_captured"] = True
                    vals["gps_latitude"] = ctx_lat
                    vals["gps_longitude"] = ctx_lon
                elif (current_lat == 0.0 and current_lon == 0.0) and (ctx_lat is not None and ctx_lon is not None):
                    vals["gps_captured"] = True
                    vals["gps_latitude"] = ctx_lat
                    vals["gps_longitude"] = ctx_lon
                if ctx_client_time:
                    vals["gps_client_time"] = ctx_client_time
                if ctx_client_tz:
                    vals["gps_client_tz"] = ctx_client_tz

            if self._has_valid_gps(vals.get("gps_latitude"), vals.get("gps_longitude")):
                vals["gps_captured"] = True
                vals["gps_openstreetmap_url"] = self._build_osm_url(vals.get("gps_latitude"), vals.get("gps_longitude"))

            # Final fallback from user's latest browser GPS ping.
            has_gps = self._has_valid_gps(vals.get("gps_latitude"), vals.get("gps_longitude"))
            if vals.get("res_model") == "crm.lead" and not has_gps:
                try:
                    user = self.env.user.sudo()
                    # Check if GPS fields exist in res.users (module might not be upgraded in all databases)
                    if hasattr(user, 'last_gps_recorded_at') and user.last_gps_recorded_at:
                        max_age = fields.Datetime.now() - timedelta(minutes=30)
                        if user.last_gps_recorded_at >= max_age:
                            vals["gps_captured"] = True
                            vals["gps_latitude"] = user.last_gps_latitude
                            vals["gps_longitude"] = user.last_gps_longitude
                            vals["gps_client_time"] = user.last_gps_client_time or vals.get("gps_client_time")
                            vals["gps_client_tz"] = user.last_gps_client_tz or vals.get("gps_client_tz")
                except Exception:
                    # Silently skip if GPS fields don't exist or any error occurs
                    pass
        activities = super().create(vals_list)
        activities._create_crm_activity_history()
        return activities

    def write(self, vals):
        if self._has_valid_gps(vals.get("gps_latitude"), vals.get("gps_longitude")):
            vals["gps_captured"] = True
            vals["gps_openstreetmap_url"] = self._build_osm_url(vals.get("gps_latitude"), vals.get("gps_longitude"))
        elif "gps_latitude" in vals or "gps_longitude" in vals:
            vals["gps_openstreetmap_url"] = False
        result = super().write(vals)

        if "kilometer" in vals:
            histories = self.env["crm.activity.history"].sudo().search([("activity_id", "in", self.ids)])
            if histories:
                histories.write({"kilometer": vals.get("kilometer") or 0.0})
        return result

    def action_feedback(self, feedback=False, attachment_ids=None):
        crm_activities = self.filtered(lambda a: a.res_model == "crm.lead")
        if not crm_activities:
            return super().action_feedback(feedback=feedback, attachment_ids=attachment_ids)

        ctx = self.env.context
        gps_captured = bool(ctx.get("gps_captured"))
        gps_latitude = ctx.get("gps_latitude")
        gps_longitude = ctx.get("gps_longitude")
        gps_url = ctx.get("gps_openstreetmap_url")
        gps_done_client_time = ctx.get("gps_done_client_time")
        gps_done_client_tz = ctx.get("gps_done_client_tz")

        extra_line = False
        has_ctx_gps = self._has_valid_gps(gps_latitude, gps_longitude)
        if has_ctx_gps:
            gps_captured = True
            if not gps_url:
                gps_url = self._build_osm_url(gps_latitude, gps_longitude)

        if gps_captured and gps_latitude is not None and gps_longitude is not None:
            extra_line = _(
                "Update at GPS location: %(lat)s, %(lon)s%(url)s",
                lat=gps_latitude,
                lon=gps_longitude,
                url=(" - %s" % gps_url) if gps_url else "",
            )

        new_feedback = feedback or ""
        if extra_line:
            new_feedback = ("%s\n%s" % (new_feedback, extra_line)).strip()

        crm_activities._mark_crm_activity_history_done(
            feedback=new_feedback,
            gps_captured=gps_captured,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            gps_url=gps_url,
            client_time=gps_done_client_time,
            client_tz=gps_done_client_tz,
        )
        return super().action_feedback(feedback=new_feedback, attachment_ids=attachment_ids)

    def _create_crm_activity_history(self):
        history_model = self.env["crm.activity.history"].sudo()
        histories = []
        for activity in self:
            if activity.res_model != "crm.lead":
                continue
            has_gps = self._has_valid_gps(activity.gps_latitude, activity.gps_longitude)
            schedule_url = activity.gps_openstreetmap_url if has_gps else False
            histories.append(
                {
                    "name": activity.activity_type_id.display_name or activity.summary or _("Activity"),
                    "activity_id": activity.id,
                    "lead_id": activity.res_id,
                    "activity_type_id": activity.activity_type_id.id,
                    "assigned_user_id": activity.user_id.id,
                    "created_by_id": self.env.user.id,
                    "summary": activity.summary,
                    "note": activity.note,
                    "kilometer": activity.kilometer,
                    "date_deadline": activity.date_deadline,
                    "scheduled_at": fields.Datetime.now(),
                    "state": "scheduled",
                    "schedule_gps_latitude": activity.gps_latitude if has_gps else False,
                    "schedule_gps_longitude": activity.gps_longitude if has_gps else False,
                    "schedule_gps_url": schedule_url,
                    "schedule_client_time": activity.gps_client_time or False,
                    "schedule_client_tz": activity.gps_client_tz or False,
                }
            )
        if histories:
            history_model.create(histories)

    def _mark_crm_activity_history_done(
        self,
        feedback,
        gps_captured=False,
        gps_latitude=None,
        gps_longitude=None,
        gps_url=None,
        client_time=None,
        client_tz=None,
    ):
        history_model = self.env["crm.activity.history"].sudo()
        for activity in self:
            history = history_model.search([("activity_id", "=", activity.id)], limit=1, order="id desc")
            vals = {
                "state": "done",
                "done_at": fields.Datetime.now(),
                "feedback": feedback or False,
                "done_client_time": client_time or False,
                "done_client_tz": client_tz or False,
            }
            if gps_captured and gps_latitude is not None and gps_longitude is not None:
                vals.update(
                    {
                        "done_gps_latitude": gps_latitude,
                        "done_gps_longitude": gps_longitude,
                        "done_gps_url": gps_url or False,
                    }
                )
            if history:
                history.write(vals)
            else:
                vals.update(
                    {
                        "name": activity.activity_type_id.display_name or activity.summary or _("Activity"),
                        "activity_id": activity.id,
                        "lead_id": activity.res_id,
                        "activity_type_id": activity.activity_type_id.id,
                        "assigned_user_id": activity.user_id.id,
                        "created_by_id": self.env.user.id,
                        "summary": activity.summary,
                        "note": activity.note,
                        "kilometer": activity.kilometer,
                        "date_deadline": activity.date_deadline,
                        "scheduled_at": fields.Datetime.now(),
                    }
                )
                history_model.create(vals)
