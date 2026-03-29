from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    last_gps_latitude = fields.Float(string="Last GPS Latitude", digits=(9, 6), readonly=True)
    last_gps_longitude = fields.Float(string="Last GPS Longitude", digits=(9, 6), readonly=True)
    last_gps_client_time = fields.Char(string="Last GPS Client Time", readonly=True)
    last_gps_client_tz = fields.Char(string="Last GPS Client TZ", readonly=True)
    last_gps_recorded_at = fields.Datetime(string="Last GPS Recorded At", readonly=True)
