from odoo import fields, models


class CrmActivityHistory(models.Model):
    _name = "crm.activity.history"
    _description = "CRM Activity History"
    _order = "scheduled_at desc, id desc"

    name = fields.Char(string="Activity", required=True)
    activity_id = fields.Many2one("mail.activity", string="Activity Record", ondelete="set null")
    lead_id = fields.Many2one("crm.lead", string="Lead/Opportunity", required=True, ondelete="cascade", index=True)
    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        related="lead_id.business_category_id",
        store=True,
        readonly=True,
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        related="lead_id.team_id",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="lead_id.company_id",
        store=True,
        readonly=True,
    )
    activity_type_id = fields.Many2one("mail.activity.type", string="Activity Type", readonly=True)
    assigned_user_id = fields.Many2one("res.users", string="Assigned To", readonly=True)
    created_by_id = fields.Many2one("res.users", string="Created By", readonly=True)
    summary = fields.Char(string="Summary", readonly=True)
    note = fields.Html(string="Scheduled Note", readonly=True)
    date_deadline = fields.Date(string="Deadline", readonly=True)
    scheduled_at = fields.Datetime(string="Scheduled At", readonly=True)

    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done")],
        string="Status",
        default="scheduled",
        required=True,
        index=True,
        readonly=True,
    )
    done_at = fields.Datetime(string="Done At", readonly=True)
    feedback = fields.Text(string="Done Feedback", readonly=True)

    schedule_gps_latitude = fields.Float(string="Schedule GPS Latitude", digits=(16, 6), readonly=True)
    schedule_gps_longitude = fields.Float(string="Schedule GPS Longitude", digits=(16, 6), readonly=True)
    schedule_gps_url = fields.Char(string="Schedule OpenStreetMap", readonly=True)
    schedule_client_time = fields.Char(string="Schedule Local Time", readonly=True)
    schedule_client_tz = fields.Char(string="Schedule Local TZ", readonly=True)
    done_gps_latitude = fields.Float(string="Done GPS Latitude", digits=(16, 6), readonly=True)
    done_gps_longitude = fields.Float(string="Done GPS Longitude", digits=(16, 6), readonly=True)
    done_gps_url = fields.Char(string="Done OpenStreetMap", readonly=True)
    done_client_time = fields.Char(string="Done Local Time", readonly=True)
    done_client_tz = fields.Char(string="Done Local TZ", readonly=True)
