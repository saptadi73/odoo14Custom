# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
    line_ids = fields.One2many(
        'scada.equipment.oee.line',
        'oee_id',
        string='Consumption Details Per Silo',
        readonly=True
    )
    avg_silo_oee_percent = fields.Float(
        string='Avg Silo OEE %',
        digits=(16, 3),
        compute='_compute_deviation_kpis',
        store=True
    )
    max_abs_deviation_percent = fields.Float(
        string='Max |Deviation| %',
        digits=(16, 3),
        compute='_compute_deviation_kpis',
        store=True
    )
    deviation_alert_count = fields.Integer(
        string='Deviation Alerts',
        compute='_compute_deviation_kpis',
        store=True
    )

    _sql_constraints = [
        ('mo_unique', 'unique(manufacturing_order_id)',
         'OEE summary already exists for this manufacturing order.')
    ]

    @staticmethod
    def _safe_ratio(numerator, denominator):
        return (numerator / denominator * 100.0) if denominator else 0.0

    @staticmethod
    def _calc_deviation_percent(actual_qty, target_qty):
        if not target_qty:
            return 0.0 if not actual_qty else 100.0
        return ((actual_qty - target_qty) / target_qty) * 100.0

    @staticmethod
    def _calc_silo_oee_from_deviation(deviation_percent):
        # Material efficiency per silo; 100% when exactly on target.
        score = 100.0 - abs(deviation_percent)
        return max(0.0, score)

    @staticmethod
    def _get_deviation_level(deviation_percent):
        abs_dev = abs(deviation_percent)
        if abs_dev <= 2.0:
            return 'normal'
        if abs_dev <= 5.0:
            return 'warning'
        return 'critical'

    @api.depends('line_ids.deviation_percent', 'line_ids.oee_silo_percent')
    def _compute_deviation_kpis(self):
        for record in self:
            lines = record.line_ids
            if not lines:
                record.avg_silo_oee_percent = 0.0
                record.max_abs_deviation_percent = 0.0
                record.deviation_alert_count = 0
                continue

            deviations = [abs(line.deviation_percent or 0.0) for line in lines]
            oee_scores = [line.oee_silo_percent or 0.0 for line in lines]
            record.avg_silo_oee_percent = sum(oee_scores) / len(oee_scores)
            record.max_abs_deviation_percent = max(deviations)
            record.deviation_alert_count = len(
                lines.filtered(lambda l: abs(l.deviation_percent or 0.0) > 2.0)
            )

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
            'line_ids': cls._prepare_consumption_lines_from_mo(mo),
        }

    def _build_consumption_line_commands(self):
        self.ensure_one()
        if not self.manufacturing_order_id:
            return []
        return self._prepare_consumption_lines_from_mo(self.manufacturing_order_id)

    def action_rebuild_consumption_lines(self):
        """Rebuild detail per silo from current MO raw moves."""
        for record in self:
            commands = record._build_consumption_line_commands()
            record.write({'line_ids': [(5, 0, 0)] + commands})
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Backward-safe: ensure detail lines exist when OEE created from non-standard flow.
        for record in records.filtered(lambda r: not r.line_ids and r.manufacturing_order_id):
            commands = record._build_consumption_line_commands()
            if commands:
                record.write({'line_ids': commands})
        return records

    @classmethod
    def _prepare_consumption_lines_from_mo(cls, mo):
        line_map = {}

        def _ensure_equipment_bucket(equipment):
            key = equipment.id if equipment else 0
            if key not in line_map:
                line_map[key] = {
                    'equipment_id': equipment.id if equipment else False,
                    'equipment_code': equipment.equipment_code if equipment else 'UNMAPPED',
                    'equipment_name': equipment.name if equipment else 'Unmapped',
                    'qty_to_consume': 0.0,
                    'qty_consumed': 0.0,
                    'material_count': 0,
                }
            return line_map[key]

        def _is_silo_equipment(equipment):
            return bool(equipment and equipment.equipment_type == 'silo')

        # 1) Target per silo from BoM (so deviation compares against formula target, not split moves).
        if mo.bom_id and mo.bom_id.product_qty:
            for bom_line in mo.bom_id.bom_line_ids:
                equipment = bom_line.scada_equipment_id
                if not _is_silo_equipment(equipment):
                    continue
                bucket = _ensure_equipment_bucket(equipment)
                planned_qty = (
                    (bom_line.product_qty / mo.bom_id.product_qty) * (mo.product_qty or 0.0)
                )
                bucket['qty_to_consume'] += planned_qty
                bucket['material_count'] += 1

        # 2) Actual per silo from stock move done qty (includes overconsumption/additional lines).
        for move in mo.move_raw_ids.filtered(lambda m: m.state != 'cancel'):
            equipment = move.scada_equipment_id
            if not _is_silo_equipment(equipment):
                continue
            bucket = _ensure_equipment_bucket(equipment)
            bucket['qty_consumed'] += move.quantity_done or 0.0

        line_commands = []
        for data in line_map.values():
            qty_to_consume = data['qty_to_consume']
            qty_consumed = data['qty_consumed']
            deviation_percent = cls._calc_deviation_percent(qty_consumed, qty_to_consume)
            oee_silo_percent = cls._calc_silo_oee_from_deviation(deviation_percent)
            line_commands.append((0, 0, {
                'equipment_id': data['equipment_id'],
                'equipment_code': data['equipment_code'],
                'equipment_name': data['equipment_name'],
                'qty_to_consume': qty_to_consume,
                'qty_consumed': qty_consumed,
                'variance_qty': qty_consumed - qty_to_consume,
                'consumption_ratio': cls._safe_ratio(qty_consumed, qty_to_consume),
                'deviation_percent': deviation_percent,
                'oee_silo_percent': oee_silo_percent,
                'deviation_level': cls._get_deviation_level(deviation_percent),
                'material_count': data['material_count'],
            }))
        return line_commands


class ScadaEquipmentOeeLine(models.Model):
    _name = 'scada.equipment.oee.line'
    _description = 'SCADA Equipment OEE Consumption Detail'
    _order = 'id'

    oee_id = fields.Many2one(
        'scada.equipment.oee',
        string='OEE Summary',
        required=True,
        ondelete='cascade'
    )
    equipment_id = fields.Many2one(
        'scada.equipment',
        string='Silo / Equipment',
        ondelete='set null'
    )
    equipment_code = fields.Char(
        string='Equipment Code',
        required=True
    )
    equipment_name = fields.Char(
        string='Equipment Name',
        required=True
    )
    qty_to_consume = fields.Float(
        string='To Consume',
        digits=(12, 3)
    )
    qty_consumed = fields.Float(
        string='Actual Consumed',
        digits=(12, 3)
    )
    variance_qty = fields.Float(
        string='Variance',
        digits=(12, 3)
    )
    consumption_ratio = fields.Float(
        string='Consumption Ratio %',
        digits=(16, 3)
    )
    deviation_percent = fields.Float(
        string='Deviation %',
        digits=(16, 3)
    )
    oee_silo_percent = fields.Float(
        string='OEE Silo %',
        digits=(16, 3)
    )
    deviation_level = fields.Selection(
        [
            ('normal', 'Normal'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        string='Deviation Level'
    )
    material_count = fields.Integer(
        string='Material Lines'
    )
