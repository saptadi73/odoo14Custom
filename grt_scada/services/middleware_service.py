"""
Middleware Service
Business logic untuk komunikasi dengan middleware dan JSON-RPC endpoints

Simplified untuk JSON-RPC - semua static methods dihapus
Fokus pada instance methods untuk business logic
"""

import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)


class MiddlewareService:
    """Service untuk manage komunikasi dengan middleware"""

    def __init__(self, env):
        self.env = env

    # ===== Instance Methods (Business Logic) =====

    def send_mo_list_to_middleware(self, equipment_code, data_format='json'):
        """
        Get MO list dan send ke middleware via API call

        Args:
            equipment_code: Equipment code
            data_format: Format data (json, xml, csv)
        """
        try:
            # Get equipment
            equipment = self.env['scada.equipment'].search([
                ('equipment_code', '=', equipment_code)
            ], limit=1)

            if not equipment:
                _logger.error(f'Equipment {equipment_code} not found')
                return False

            # Get pending MO data
            mo_records = self.env['scada.mo.data'].search([
                ('equipment_id', '=', equipment.id),
                ('sync_status', '!=', 'synced'),
            ])

            if not mo_records:
                _logger.info(f'No pending MO data for {equipment_code}')
                return True

            # Format data
            mo_list = [mo._prepare_data_for_middleware() for mo in mo_records]

            # Send to middleware (stub implementation)
            result = self._send_to_middleware(
                equipment=equipment,
                endpoint='mo-list',
                data=mo_list,
                format=data_format
            )

            if result:
                # Mark as synced
                for mo in mo_records:
                    mo.mark_sent_to_middleware()
                _logger.info(f'Sent {len(mo_records)} MO records to {equipment_code}')

            return result

        except Exception as e:
            _logger.error(f'Error sending MO list: {str(e)}')
            return False

    def process_material_consumption(self, consumption_data):
        """
        Process material consumption data dari middleware

        Args:
            consumption_data: Dict dengan material consumption info
        """
        try:
            result = self.env['scada.material.consumption'].create_from_api(consumption_data)
            if result.get('status') == 'success':
                return result.get('record_id')
            raise ValueError(result.get('message') or 'Unknown error')
        except Exception as e:
            _logger.error(f'Error processing material consumption: {str(e)}')
            raise

    def _send_to_middleware(self, equipment, endpoint, data, format='json'):
        """
        Send data ke middleware

        Stub implementation - integrate dengan actual middleware
        """
        try:
            if not equipment.ip_address or not equipment.port:
                _logger.warning(f'Equipment {equipment.name} tidak memiliki connection info')
                return False

            # TODO: Implement actual HTTP call ke middleware
            # url = f'http://{equipment.ip_address}:{equipment.port}/{endpoint}'
            # response = requests.post(url, json=data)

            _logger.info(
                f'[STUB] Would send to {equipment.ip_address}:{equipment.port}/{endpoint}'
            )
            return True

        except Exception as e:
            _logger.error(f'Error sending to middleware: {str(e)}')
            return False

    def retry_failed_syncs(self):
        """Retry semua failed syncs"""
        try:
            # Get failed records
            failed_consumptions = self.env['scada.material.consumption'].search([
                ('sync_status', '=', 'error')
            ])

            failed_mo_data = self.env['scada.mo.data'].search([
                ('sync_status', '=', 'error')
            ])

            count = 0
            for record in list(failed_consumptions) + list(failed_mo_data):
                record.retry_sync()
                count += 1

            _logger.info(f'Retried {count} failed sync records')
            return count

        except Exception as e:
            _logger.error(f'Error retrying failed syncs: {str(e)}')
            return 0

    def sync_equipment_status(self):
        """Sync status dari semua equipment"""
        try:
            equipment_list = self.env['scada.equipment'].search([
                ('is_active', '=', True)
            ])

            for equipment in equipment_list:
                # Test connection
                equipment.test_connection()

            return True

        except Exception as e:
            _logger.error(f'Error syncing equipment status: {str(e)}')
            return False

