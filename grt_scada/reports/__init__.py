"""
Reports for SCADA Material Consumption
"""

from odoo import models, fields
from datetime import datetime, timedelta


class ScadaMaterialConsumptionReport(models.AbstractModel):
    """Material Consumption Report"""
    _name = 'report.grt_scada.material_consumption_report'

    def _get_report_data(self, data):
        """Prepare report data"""
        consumption_records = self.env['scada.material.consumption'].search([])
        
        report_lines = []
        for record in consumption_records:
            report_lines.append({
                'date': record.timestamp.date(),
                'equipment': record.equipment_id.name,
                'material': record.material_id.name,
                'quantity': record.quantity,
                'unit': record.unit_of_measure.name,
                'status': record.status,
            })

        return report_lines

    def _get_summary(self, data):
        """Get summary statistics"""
        consumptions = self.env['scada.material.consumption'].search([])
        
        total_quantity = sum(c.quantity for c in consumptions)
        total_records = len(consumptions)
        
        return {
            'total_records': total_records,
            'total_quantity': total_quantity,
        }
