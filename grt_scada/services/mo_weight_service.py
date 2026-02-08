"""
MO Weight Service
Compute target weight from BoM and store actual weight
"""

import logging

_logger = logging.getLogger(__name__)


class MoWeightService:
    """Service for MO weight tracking"""

    def __init__(self, env):
        self.env = env

    def create_mo_weight(self, payload):
        try:
            mo_value = payload.get('mo_id') or payload.get('manufacturing_order_id')
            if not mo_value:
                return {'status': 'error', 'message': 'mo_id is required'}

            mo_record = self._find_mo(mo_value)
            if not mo_record:
                return {'status': 'error', 'message': f'MO not found: {mo_value}'}

            if not mo_record.bom_id or not mo_record.bom_id.product_qty:
                return {'status': 'error', 'message': 'BoM not found for MO'}

            weight_actual = payload.get('weight_actual')
            if weight_actual is None:
                return {'status': 'error', 'message': 'weight_actual is required'}

            try:
                weight_actual = float(weight_actual)
            except (TypeError, ValueError):
                return {'status': 'error', 'message': 'weight_actual must be a number'}

            target_weight = self._compute_target_weight(mo_record)

            record = self.env['scada.mo.weight'].create({
                'manufacturing_order_id': mo_record.id,
                'target_weight': target_weight,
                'weight_actual': weight_actual,
                'timestamp': payload.get('timestamp') or False,
                'notes': payload.get('notes'),
            })

            return {
                'status': 'success',
                'message': 'MO weight recorded successfully',
                'record_id': record.id,
                'mo_id': mo_record.name,
                'target_weight': target_weight,
                'weight_actual': weight_actual,
            }
        except Exception as e:
            _logger.error(f'Error creating MO weight: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    def get_mo_weights(self, mo_value=None, limit=50, offset=0):
        try:
            domain = []

            if mo_value:
                mo_record = self._find_mo(mo_value)
                if not mo_record:
                    return {'status': 'error', 'message': f'MO not found: {mo_value}'}
                domain.append(('manufacturing_order_id', '=', mo_record.id))

            records = self.env['scada.mo.weight'].search(
                domain,
                limit=limit,
                offset=offset,
                order='timestamp desc, id desc'
            )

            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'mo_id': record.manufacturing_order_id.name,
                    'product_id': record.manufacturing_order_id.product_id.id,
                    'target_weight': record.target_weight,
                    'weight_actual': record.weight_actual,
                    'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                    'notes': record.notes,
                })

            return {
                'status': 'success',
                'count': len(data),
                'data': data,
            }
        except Exception as e:
            _logger.error(f'Error getting MO weights: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    def _find_mo(self, mo_value):
        if isinstance(mo_value, int) or str(mo_value).isdigit():
            mo_record = self.env['mrp.production'].browse(int(mo_value))
        else:
            mo_record = self.env['mrp.production'].search([
                ('name', '=', str(mo_value))
            ], limit=1)
        return mo_record if mo_record and mo_record.exists() else False

    def _compute_target_weight(self, mo_record):
        """Sum(component.weight * qty_bom_scaled) for MO quantity."""
        target_weight = 0.0
        bom = mo_record.bom_id
        scale = mo_record.product_qty / bom.product_qty
        for line in bom.bom_line_ids:
            component_weight = line.product_id.weight or 0.0
            target_weight += component_weight * (line.product_qty * scale)
        return target_weight
