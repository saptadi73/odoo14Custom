"""
Deprecated SCADA MO Data model.
Kept to allow module upgrades to clean up old records safely.
"""

from odoo import models


class ScadaMoDataDeprecated(models.Model):
    _name = 'scada.mo.data'
    _description = 'SCADA MO Data (Deprecated)'
    _inherit = 'scada.base'
