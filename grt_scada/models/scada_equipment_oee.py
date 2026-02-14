# -*- coding: utf-8 -*-

from odoo import models, fields


class ScadaEquipmentOee(models.Model):
    _name = 'scada.equipment.oee'
    _description = 'SCADA Equipment OEE Summary'
    _order = 'date_done desc, id desc'
    _rec_name = 'mo_name'

    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        required=True,
        ondelete='restrict'
    )
    mo_name = fields.Char(
        string='MO Name',
        related='manufacturing_order_id.name',
        store=True,
        readonly=True
    )
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Equipment',
        required=True,
        ondelete='restrict'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='manufacturing_order_id.product_id',
        store=True,
        readonly=True
    )
    date_done = fields.Datetime(
        string='Done Date',
        default=fields.Datetime.now,
        required=True
    )

    qty_planned = fields.Float(
        string='Planned Qty (BoM)',
        digits=(12, 3)
    )
    qty_finished = fields.Float(
        string='Actual Finished Qty',
        digits=(12, 3)
    )
    qty_bom_consumption = fields.Float(
        string='BoM Consumption (Total)',
        digits=(12, 3)
    )
    qty_actual_consumption = fields.Float(
        string='Actual Consumption (Total)',
        digits=(12, 3)
    )

    variance_finished = fields.Float(
        string='Finished Variance',
        digits=(12, 3)
    )
    variance_consumption = fields.Float(
        string='Consumption Variance',
        digits=(12, 3)
    )

    yield_percent = fields.Float(
        string='Yield %',
        digits=(16, 3)
    )
    consumption_ratio = fields.Float(
        string='Consumption Ratio %',
        digits=(16, 3)
    )

    notes = fields.Text(string='Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('mo_unique', 'unique(manufacturing_order_id)',
         'OEE summary already exists for this manufacturing order.')
    ]

    @staticmethod
    def _safe_ratio(numerator, denominator):
        return (numerator / denominator * 100.0) if denominator else 0.0

    @classmethod
    def prepare_from_mo(cls, mo, equipment):
        finished_qty = sum(
            move.quantity_done for move in mo.move_finished_ids
            if move.state != 'cancel'
        )
        actual_consumed = sum(
            move.quantity_done for move in mo.move_raw_ids
            if move.state != 'cancel'
        )

        bom_consumption = 0.0
        if mo.bom_id and mo.bom_id.product_qty:
            for line in mo.bom_id.bom_line_ids:
                bom_consumption += (
                    (line.product_qty / mo.bom_id.product_qty) * mo.product_qty
                )

        planned_qty = mo.product_qty or 0.0
        variance_finished = finished_qty - planned_qty
        variance_consumption = actual_consumed - bom_consumption

        return {
            'manufacturing_order_id': mo.id,
            'equipment_id': equipment.id,
            'date_done': mo.date_finished or mo.date_planned_finished or fields.Datetime.now(),
            'qty_planned': planned_qty,
            'qty_finished': finished_qty,
            'qty_bom_consumption': bom_consumption,
            'qty_actual_consumption': actual_consumed,
            'variance_finished': variance_finished,
            'variance_consumption': variance_consumption,
            'yield_percent': cls._safe_ratio(finished_qty, planned_qty),
            'consumption_ratio': cls._safe_ratio(actual_consumed, bom_consumption),
            'company_id': mo.company_id.id,
        }
