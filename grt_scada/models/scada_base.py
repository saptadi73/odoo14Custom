"""
SCADA Base Model
Base class untuk semua SCADA models dengan common fields dan methods
"""

from odoo import models, fields, api
from datetime import datetime


class ScadaBase(models.AbstractModel):
    """Abstract base class untuk SCADA models"""
    _name = 'scada.base'
    _description = 'SCADA Base Model'

    # Common fields untuk semua SCADA records
    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        readonly=True,
        help='Waktu record dibuat'
    )
    updated_at = fields.Datetime(
        string='Updated At',
        default=fields.Datetime.now,
        help='Waktu record terakhir diupdate'
    )
    external_id = fields.Char(
        string='External ID',
        help='ID dari sistem eksternal (Middleware/PLC)'
    )
    source_system = fields.Selection(
        [
            ('middleware', 'Middleware'),
            ('plc', 'PLC OMRON'),
            ('odoo', 'Odoo'),
            ('manual', 'Manual Entry'),
        ],
        string='Source System',
        default='middleware',
        help='Sistem asal data'
    )
    sync_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('synced', 'Synced'),
            ('error', 'Error'),
            ('failed', 'Failed'),
        ],
        string='Sync Status',
        default='pending',
        help='Status sinkronisasi dengan sistem eksternal'
    )
    error_message = fields.Text(
        string='Error Message',
        help='Pesan error jika terjadi kesalahan'
    )

    @api.model
    def create(self, vals):
        """Override create untuk set timestamp"""
        vals.update({
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        })
        return super().create(vals)

    def write(self, vals):
        """Override write untuk update timestamp"""
        vals.update({
            'updated_at': datetime.now(),
        })
        return super().write(vals)

    def log_error(self, error_msg):
        """Helper method untuk log error"""
        self.write({
            'sync_status': 'error',
            'error_message': error_msg,
        })

    def mark_synced(self):
        """Mark record sebagai successfully synced"""
        self.write({
            'sync_status': 'synced',
            'error_message': False,
        })
