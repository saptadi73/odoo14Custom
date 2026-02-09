"""
Validation Service
Validate data dari middleware sebelum diproses

XML-RPC Compatible - bisa dipanggil via:
    models.execute_kw(db, uid, password, 'scada.material.consumption', 
                     'validate_payload', [payload_dict])
"""

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ValidationService:
    """Service untuk validasi data"""

    @staticmethod
    def validate_material_consumption_data(env, data):
        """
        Validate material consumption data
        
        Args:
            env: Odoo environment
            data: Dict dengan material consumption info
            
        Returns:
            (is_valid, error_message)
        """
        errors = []

        # Check required fields
        required_fields = {
            'equipment_id': 'Equipment ID',
            'quantity': 'Quantity',
            'timestamp': 'Timestamp',
        }

        for field, label in required_fields.items():
            if field not in data or data[field] is None:
                errors.append(f'{label} is required')

        if not data.get('material_id') and not data.get('product_id') and not data.get('product_tmpl_id'):
            errors.append('Product ID or Product Template ID is required')

        # Validate equipment exists
        if data.get('equipment_id'):
            equipment = env['scada.equipment'].search([
                ('equipment_code', '=', data['equipment_id'])
            ])
            if not equipment:
                errors.append(f'Equipment "{data["equipment_id"]}" not found')

        # Validate material exists
        material_id = data.get('material_id') or data.get('product_id')
        product_tmpl_id = data.get('product_tmpl_id')
        if material_id:
            try:
                material_id = int(material_id)
                material = env['product.product'].browse(material_id)
                if not material.exists():
                    errors.append(f'Product ID "{material_id}" not found')
            except (TypeError, ValueError):
                errors.append('Product ID must be a number')
        elif product_tmpl_id:
            try:
                product_tmpl_id = int(product_tmpl_id)
                template = env['product.template'].browse(product_tmpl_id)
                if not template.exists():
                    errors.append(f'Product Template ID "{product_tmpl_id}" not found')
                elif not template.product_variant_id:
                    errors.append(f'Product Template "{product_tmpl_id}" has no variant')
            except (TypeError, ValueError):
                errors.append('Product Template ID must be a number')

        # Validate manufacturing order (required)
        mo_value = data.get('mo_id') or data.get('manufacturing_order_id')
        if not mo_value:
            errors.append('MO ID is required')
        else:
            try:
                if isinstance(mo_value, int) or str(mo_value).isdigit():
                    mo_record = env['mrp.production'].browse(int(mo_value))
                else:
                    mo_record = env['mrp.production'].search([
                        ('name', '=', str(mo_value))
                    ], limit=1)
                if not mo_record or not mo_record.exists():
                    errors.append(f'Manufacturing Order "{mo_value}" not found')
            except Exception:
                errors.append('Invalid MO identifier')

        # Validate quantity
        if data.get('quantity'):
            try:
                qty = float(data['quantity'])
                if qty <= 0:
                    errors.append('Quantity must be positive')
            except ValueError:
                errors.append('Quantity must be a number')

        # Validate timestamp
        if data.get('timestamp'):
            try:
                ts = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                if ts > datetime.now():
                    errors.append('Timestamp cannot be in the future')
            except ValueError:
                errors.append('Invalid timestamp format')

        if errors:
            return False, '; '.join(errors)

        return True, ''

    @staticmethod
    def validate_mo_data(env, mo_data):
        """
        Validate MO data
        
        Args:
            env: Odoo environment
            mo_data: Manufacturing order data
            
        Returns:
            (is_valid, error_message)
        """
        errors = []

        # Check MO exists
        if not mo_data.get('mo_id'):
            errors.append('MO ID is required')
        else:
            mo = env['mrp.production'].search([
                ('name', '=', mo_data['mo_id'])
            ])
            if not mo:
                errors.append(f'Manufacturing Order "{mo_data["mo_id"]}" not found')

        # Check equipment jika specified
        if mo_data.get('equipment_id'):
            equipment = env['scada.equipment'].search([
                ('equipment_code', '=', mo_data['equipment_id'])
            ])
            if not equipment:
                errors.append(f'Equipment "{mo_data["equipment_id"]}" not found')

        if errors:
            return False, '; '.join(errors)

        return True, ''

    @staticmethod
    def validate_equipment_config(env, equipment_dict):
        """
        Validate equipment configuration data
        
        Args:
            env: Odoo environment
            equipment_dict: Equipment configuration
            
        Returns:
            (is_valid, error_message)
        """
        errors = []

        # Check required fields
        if not equipment_dict.get('name'):
            errors.append('Equipment name is required')

        if not equipment_dict.get('equipment_code'):
            errors.append('Equipment code is required')

        if not equipment_dict.get('equipment_type'):
            errors.append('Equipment type is required')

        # Check if equipment code is unique
        if equipment_dict.get('equipment_code'):
            existing = env['scada.equipment'].search([
                ('equipment_code', '=', equipment_dict['equipment_code'])
            ])
            if existing:
                errors.append(
                    f'Equipment code "{equipment_dict["equipment_code"]}" already exists'
                )

        # Validate protocol if provided
        valid_protocols = [
            'modbus', 'opcua', 'mqtt', 'http', 'tcp', 'other'
        ]
        if equipment_dict.get('protocol') and equipment_dict['protocol'] not in valid_protocols:
            errors.append(
                f'Invalid protocol. Must be one of: {", ".join(valid_protocols)}'
            )

        # Check IP and port if protocol requires it
        if equipment_dict.get('protocol') in ['http', 'tcp', 'modbus']:
            if not equipment_dict.get('ip_address'):
                errors.append('IP Address is required for this protocol')
            if not equipment_dict.get('port'):
                errors.append('Port is required for this protocol')

        if errors:
            return False, '; '.join(errors)

        return True, ''
