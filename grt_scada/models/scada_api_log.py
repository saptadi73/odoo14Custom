"""
SCADA API Log Model
Model untuk logging semua API calls dari middleware
"""

from odoo import models, fields, api
import json


class ScadaApiLog(models.Model):
    """Model untuk SCADA API Logs"""
    _name = 'scada.api.log'
    _description = 'SCADA API Log'
    _order = 'timestamp desc'

    # Request Info
    method = fields.Selection(
        [
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('DELETE', 'DELETE'),
            ('PATCH', 'PATCH'),
        ],
        string='HTTP Method',
        required=True,
        help='HTTP method dari request'
    )
    endpoint = fields.Char(
        string='Endpoint',
        required=True,
        help='API endpoint yang dipanggil'
    )
    request_id = fields.Char(
        string='Request ID',
        help='Unique ID untuk tracking request'
    )

    # Equipment Info
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        help='Equipment yang terkait dengan request'
    )

    # Request/Response Data
    request_data = fields.Text(
        string='Request Data',
        help='Data yang dikirim dalam request (JSON format)'
    )
    response_data = fields.Text(
        string='Response Data',
        help='Data yang dikembalikan dalam response (JSON format)'
    )

    # Status & Error
    http_status_code = fields.Integer(
        string='HTTP Status Code',
        help='HTTP response status code'
    )
    status = fields.Selection(
        [
            ('success', 'Success'),
            ('error', 'Error'),
            ('failed', 'Failed'),
            ('timeout', 'Timeout'),
        ],
        string='Status',
        required=True,
        help='Status dari API call'
    )
    error_message = fields.Text(
        string='Error Message',
        help='Error message jika terjadi error'
    )

    # Timestamp & Performance
    timestamp = fields.Datetime(
        string='Request Time',
        default=fields.Datetime.now,
        readonly=True,
        help='Waktu request dilakukan'
    )
    response_time_ms = fields.Float(
        string='Response Time (ms)',
        help='Response time dalam millisecond'
    )

    # Source Info
    source_ip = fields.Char(
        string='Source IP',
        help='IP address yang melakukan request'
    )
    user_agent = fields.Char(
        string='User Agent',
        help='User agent dari request'
    )

    notes = fields.Text(
        string='Notes',
        help='Catatan tambahan'
    )

    def get_api_logs(self, equipment_id=None, method=None, status=None):
        """Get API logs dengan filter"""
        domain = []

        if equipment_id:
            domain.append(('equipment_id', '=', equipment_id))
        if method:
            domain.append(('method', '=', method))
        if status:
            domain.append(('status', '=', status))

        return self.search(domain, order='timestamp desc')

    def get_failed_requests(self):
        """Get semua failed requests untuk retry"""
        return self.search([
            ('status', 'in', ['error', 'failed', 'timeout']),
        ], order='timestamp asc')

    def log_api_call(self, **kwargs):
        """Log API call"""
        return self.create({
            'method': kwargs.get('method', 'POST'),
            'endpoint': kwargs.get('endpoint'),
            'request_id': kwargs.get('request_id'),
            'equipment_id': kwargs.get('equipment_id'),
            'request_data': kwargs.get('request_data'),
            'response_data': kwargs.get('response_data'),
            'http_status_code': kwargs.get('http_status_code'),
            'status': kwargs.get('status', 'pending'),
            'error_message': kwargs.get('error_message'),
            'response_time_ms': kwargs.get('response_time_ms'),
            'source_ip': kwargs.get('source_ip'),
            'user_agent': kwargs.get('user_agent'),
            'notes': kwargs.get('notes'),
        })

    def cleanup_old_logs(self, days=30):
        """Delete logs lebih dari X hari"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        old_logs = self.search([
            ('timestamp', '<', cutoff_date)
        ])
        old_logs.unlink()
