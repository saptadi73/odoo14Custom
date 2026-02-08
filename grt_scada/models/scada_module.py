"""
SCADA Module Info Model
Model untuk module version dan info endpoint
"""

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ScadaModule(models.Model):
    """Model untuk SCADA Module Info"""
    _name = 'scada.module'
    _description = 'SCADA Module Info'
    _auto = False  # No database table

    @api.model
    def get_version(self):
        """
        Get SCADA module version
        
        Returns:
            Dict dengan module info
            
        XML-RPC Usage:
            models.execute_kw(db, uid, pwd, 'scada.module', 'get_version', [])
        """
        try:
            module = self.env['ir.module.module'].search([
                ('name', '=', 'grt_scada')
            ], limit=1)

            if module:
                return {
                    'status': 'success',
                    'version': module.latest_version or '1.0.0',
                    'name': 'SCADA for Odoo',
                    'state': module.state,
                }
            
            return {
                'status': 'error',
                'message': 'Module not found',
                'version': None,
                'name': None,
            }
        except Exception as e:
            _logger.error(f'Error getting module version: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
                'version': None,
                'name': None,
            }
