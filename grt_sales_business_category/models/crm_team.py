from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    sale_team_leader_id = fields.Many2one(
        "res.users",
        string="Sales Team Leader",
        help="First approval for Sales Orders in this team is handled by this user.",
    )
