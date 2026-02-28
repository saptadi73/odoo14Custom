from odoo import fields, models, api


class ScadaEquipmentFailure(models.Model):
    _name = 'scada.equipment.failure'
    _description = 'SCADA Equipment Failure'
    _order = 'date desc, id desc'

    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='restrict',
    )
    equipment_code = fields.Char(
        string='Equipment Code',
        related='equipment_id.equipment_code',
        store=True,
        readonly=True,
    )
    description = fields.Text(string='Description', required=True)
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
    )
    reported_by = fields.Many2one(
        'res.users',
        string='Reported By',
        default=lambda self: self.env.user,
        readonly=True,
    )
    duration = fields.Char(
        string='Duration (hh:mm)',
        help='Durasi failure dalam format hh:mm (contoh: 02:30 untuk 2 jam 30 menit)',
    )
    duration_minutes = fields.Integer(
        string='Duration (minutes)',
        compute='_compute_duration_minutes',
        store=True,
        help='Durasi dalam menit untuk reporting',
    )

    @api.constrains('duration')
    def _check_duration_format(self):
        """Validasi format duration hh:mm"""
        for record in self:
            if record.duration:
                import re
                # Pattern: hh:mm format (00:00 to 23:59)
                pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
                if not re.match(pattern, record.duration.strip()):
                    raise ValueError(
                        f"Format durasi '{record.duration}' tidak valid. "
                        "Gunakan format hh:mm (contoh: 02:30)"
                    )

    @api.depends('duration')
    def _compute_duration_minutes(self):
        """Konversi durasi hh:mm ke total menit"""
        for record in self:
            if record.duration:
                try:
                    hours, minutes = map(int, record.duration.strip().split(':'))
                    record.duration_minutes = hours * 60 + minutes
                except (ValueError, AttributeError):
                    record.duration_minutes = 0
            else:
                record.duration_minutes = 0

