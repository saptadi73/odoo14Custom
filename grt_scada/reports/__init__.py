"""
Reports for SCADA Material Consumption
Consumption is sourced from MO raw moves (quantity_done).
"""

from odoo import models, fields
from datetime import datetime, timedelta


class ScadaMaterialConsumptionReport(models.AbstractModel):
    """Material Consumption Report"""
    _name = 'report.grt_scada.material_consumption_report'

    def _get_report_data(self, data):
        """Prepare report data"""
        report_lines = []
        mo_records = self.env['mrp.production'].search([])

        for mo in mo_records:
            equipment_name = ''
            if getattr(mo, 'scada_equipment_id', False):
                equipment_name = mo.scada_equipment_id.name or ''
            else:
                workcenter = mo.workorder_ids[:1].workcenter_id if mo.workorder_ids else False
                if workcenter:
                    equipment = self.env['scada.equipment'].search([
                        ('production_line_id', '=', workcenter.id)
                    ], limit=1)
                    equipment_name = equipment.name if equipment else ''

            for move in mo.move_raw_ids:
                if (move.quantity_done or 0.0) <= 0:
                    continue
                report_lines.append({
                    'date': move.date.date() if move.date else None,
                    'equipment': equipment_name,
                    'material': move.product_id.name,
                    'quantity': move.quantity_done,
                    'unit': move.product_uom.name if move.product_uom else '',
                    'status': move.state,
                })

        return report_lines

    def _get_summary(self, data):
        """Get summary statistics"""
        total_quantity = 0.0
        total_records = 0
        mo_records = self.env['mrp.production'].search([])
        for mo in mo_records:
            for move in mo.move_raw_ids:
                if (move.quantity_done or 0.0) <= 0:
                    continue
                total_records += 1
                total_quantity += move.quantity_done
        
        return {
            'total_records': total_records,
            'total_quantity': total_quantity,
        }
