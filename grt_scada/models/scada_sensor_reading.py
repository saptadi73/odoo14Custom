"""
SCADA Sensor Reading Model
Model untuk real-time sensor data dari equipment
"""

from odoo import models, fields, api


class ScadaSensorReading(models.Model):
    """Model untuk SCADA Sensor Readings"""
    _name = 'scada.sensor.reading'
    _description = 'SCADA Sensor Reading'
    _order = 'timestamp desc'
    _inherit = 'scada.base'

    # Sensor Info
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='cascade',
        help='Equipment source dari sensor'
    )
    sensor_name = fields.Char(
        string='Sensor Name',
        required=True,
        help='Nama sensor (contoh: TEMP_01, PRESSURE_01)'
    )
    sensor_type = fields.Selection(
        [
            ('temperature', 'Temperature'),
            ('pressure', 'Pressure'),
            ('humidity', 'Humidity'),
            ('flow', 'Flow'),
            ('level', 'Level'),
            ('speed', 'Speed'),
            ('vibration', 'Vibration'),
            ('voltage', 'Voltage'),
            ('current', 'Current'),
            ('other', 'Other'),
        ],
        string='Sensor Type',
        required=True,
        help='Tipe sensor'
    )

    # Sensor Reading Values
    reading_value = fields.Float(
        string='Reading Value',
        required=True,
        digits=(12, 4),
        help='Nilai pembacaan sensor'
    )
    unit = fields.Char(
        string='Unit',
        help='Unit pembacaan (°C, PSI, %, RPM, etc)'
    )
    min_threshold = fields.Float(
        string='Min Threshold',
        digits=(12, 4),
        help='Nilai minimum normal'
    )
    max_threshold = fields.Float(
        string='Max Threshold',
        digits=(12, 4),
        help='Nilai maximum normal'
    )

    # Status
    status = fields.Selection(
        [
            ('normal', 'Normal'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('error', 'Error'),
        ],
        string='Status',
        compute='_compute_status',
        store=True,
        help='Status pembacaan berdasarkan threshold'
    )

    # Timestamp
    timestamp = fields.Datetime(
        string='Reading Time',
        required=True,
        default=fields.Datetime.now,
        help='Waktu pembacaan sensor'
    )

    notes = fields.Text(
        string='Notes',
        help='Catatan tambahan'
    )

    @api.depends('reading_value', 'min_threshold', 'max_threshold')
    def _compute_status(self):
        """Compute status berdasarkan reading value dan threshold"""
        for record in self:
            value = record.reading_value
            min_thr = record.min_threshold
            max_thr = record.max_threshold

            if not min_thr or not max_thr:
                record.status = 'normal'
                continue

            if value < min_thr or value > max_thr:
                # Check jika critical (lebih jauh dari threshold)
                if value < (min_thr * 0.9) or value > (max_thr * 1.1):
                    record.status = 'critical'
                else:
                    record.status = 'warning'
            else:
                record.status = 'normal'

    def get_latest_readings(self, equipment_id, limit=10):
        """Get latest sensor readings dari equipment"""
        return self.search([
            ('equipment_id', '=', equipment_id),
        ], order='timestamp desc', limit=limit)

    def get_readings_by_sensor_type(self, equipment_id, sensor_type):
        """Get readings untuk specific sensor type"""
        return self.search([
            ('equipment_id', '=', equipment_id),
            ('sensor_type', '=', sensor_type),
        ], order='timestamp desc')
