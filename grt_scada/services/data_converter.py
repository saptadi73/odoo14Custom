"""
Data Converter Service
Convert format data antara Odoo dan middleware/PLC

XML-RPC Compatible - bisa dipanggil via:
    models.execute_kw(db, uid, password, 'scada.data.converter', 'convert_to_json', [data])
"""

import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class DataConverter:
    """Service untuk convert format data"""

    @staticmethod
    def convert_to_json(data):
        """Convert data ke JSON format"""
        try:
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            _logger.error(f'Error converting to JSON: {str(e)}')
            return None

    @staticmethod
    def convert_from_json(json_str):
        """Convert dari JSON string ke dict"""
        try:
            return json.loads(json_str)
        except Exception as e:
            _logger.error(f'Error converting from JSON: {str(e)}')
            return None

    @staticmethod
    def convert_to_csv(data_list, headers=None):
        """Convert list of data ke CSV format"""
        try:
            if not data_list:
                return ''

            if headers is None:
                headers = list(data_list[0].keys())

            csv_lines = [','.join(headers)]

            for row in data_list:
                values = []
                for header in headers:
                    value = row.get(header, '')
                    # Escape quotes dalam string
                    value_str = str(value).replace('"', '""')
                    values.append(f'"{value_str}"')
                csv_lines.append(','.join(values))

            return '\n'.join(csv_lines)

        except Exception as e:
            _logger.error(f'Error converting to CSV: {str(e)}')
            return None

    @staticmethod
    def convert_from_csv(csv_str, headers=None):
        """Convert dari CSV string ke list of dicts"""
        try:
            import csv
            from io import StringIO

            lines = StringIO(csv_str.strip())
            reader = csv.reader(lines)

            if headers is None:
                headers = next(reader)

            data_list = []
            for row in reader:
                data_dict = {}
                for i, header in enumerate(headers):
                    data_dict[header] = row[i] if i < len(row) else ''
                data_list.append(data_dict)

            return data_list

        except Exception as e:
            _logger.error(f'Error converting from CSV: {str(e)}')
            return None

    @staticmethod
    def convert_equipment_status_to_middleware_format(env, equipment_id):
        """
        Convert equipment status ke format middleware
        
        Args:
            env: Odoo environment
            equipment_id: Equipment record ID
        """
        equipment = env['scada.equipment'].browse(equipment_id)
        if not equipment.exists():
            return None
            
        return {
            'equipment_id': equipment.equipment_code,
            'name': equipment.name,
            'status': equipment.connection_status,
            'last_connected': equipment.last_connected.isoformat() if equipment.last_connected else None,
            'is_active': equipment.is_active,
        }

    @staticmethod
    def convert_material_consumption_to_plc_format(env, consumption_id):
        """
        Convert material consumption ke format PLC
        
        Args:
            env: Odoo environment
            consumption_id: Material consumption record ID
        """
        consumption = env['scada.material.consumption'].browse(consumption_id)
        if not consumption.exists():
            return None
            
        return {
            'equipment_id': consumption.equipment_id.equipment_code,
            'material_id': consumption.material_id.default_code,
            'material_name': consumption.material_id.name,
            'quantity': float(consumption.quantity),
            'unit': consumption.unit_of_measure.name if consumption.unit_of_measure else '',
            'timestamp': consumption.timestamp.isoformat(),
            'status': consumption.status,
        }

    @staticmethod
    def convert_mo_to_plc_format(env, mo_record_id):
        """
        Convert MO data ke format PLC
        
        Args:
            env: Odoo environment
            mo_record_id: MO Data record ID
        """
        mo_record = env['scada.mo.data'].browse(mo_record_id)
        if not mo_record.exists():
            return None
            
        return mo_record._prepare_data_for_middleware()

    @staticmethod
    def parse_middleware_error_response(response):
        """Parse error response dari middleware"""
        try:
            if isinstance(response, dict):
                return response.get('message') or response.get('error')
            elif isinstance(response, str):
                try:
                    data = json.loads(response)
                    return data.get('message') or data.get('error')
                except:
                    return response
            return str(response)
        except Exception as e:
            return f'Unknown error: {str(e)}'
