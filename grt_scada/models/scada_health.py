"""
SCADA Health Check Model
Model untuk health check endpoint
"""

from odoo import models, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ScadaHealth(models.Model):
    """Model untuk SCADA Health Check"""
    _name = 'scada.health'
    _description = 'SCADA Health Check'
    _auto = False  # No database table

    @api.model
    def check(self):
        """
        Health check endpoint
        
        Returns:
            Dict dengan health status
            
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.health', 'check', [])
        """
        try:
            return {
                'status': 'ok',
                'message': 'SCADA Module is running',
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            _logger.error(f'Health check error: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            }
