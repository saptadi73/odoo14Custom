"""
MRP Production extensions for SCADA equipment defaults.
"""

import logging

from odoo import models, fields, api
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    scada_equipment_id = fields.Many2one(
        'scada.equipment',
        string='SCADA Equipment',
        help='Defaulted from BoM, can be changed per MO for operational needs.'
    )

    def _get_scada_bom_for_product(self):
        self.ensure_one()
        if not self.product_id:
            return self.env['mrp.bom']
        return self.env['mrp.bom']._bom_find(
            product=self.product_id,
            company_id=(self.company_id or self.env.company).id,
            bom_type='normal',
        )

    @api.onchange('product_id', 'bom_id')
    def _onchange_scada_equipment_defaults(self):
        for record in self:
            bom = record.bom_id
            if not bom and record.product_id:
                bom = record._get_scada_bom_for_product()
                if bom:
                    record.bom_id = bom
            if bom and not record.scada_equipment_id:
                record.scada_equipment_id = bom.scada_equipment_id
            # Mirror bulk behavior in the draft form so component lines show
            # their equipment before the MO is saved/confirmed.
            if record.move_raw_ids:
                record._sync_scada_equipment_to_moves()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('scada_equipment_id'):
                continue
            bom_id = vals.get('bom_id')
            if bom_id:
                bom = self.env['mrp.bom'].browse(bom_id)
                if bom and bom.scada_equipment_id:
                    vals['scada_equipment_id'] = bom.scada_equipment_id.id
        records = super().create(vals_list)
        # Sync SCADA equipment from BoM lines to stock moves after creation
        records._sync_scada_equipment_to_moves()
        return records

    def _sync_scada_equipment_to_moves(self):
        """Sync SCADA equipment from BoM lines to corresponding raw material moves"""
        for mo in self:
            if not mo.bom_id:
                continue

            bom_lines_by_product = {}
            for bom_line in mo.bom_id.bom_line_ids.filtered('scada_equipment_id'):
                bom_lines_by_product.setdefault(bom_line.product_id.id, self.env['mrp.bom.line'])
                bom_lines_by_product[bom_line.product_id.id] |= bom_line

            if not bom_lines_by_product:
                continue

            # Update raw material moves that don't have scada_equipment_id yet
            for move in mo.move_raw_ids:
                if move.scada_equipment_id:
                    continue

                equipment = False
                if move.bom_line_id and move.bom_line_id.scada_equipment_id:
                    equipment = move.bom_line_id.scada_equipment_id
                else:
                    matching_bom_lines = bom_lines_by_product.get(move.product_id.id, self.env['mrp.bom.line'])
                    if len(matching_bom_lines) == 1:
                        equipment = matching_bom_lines.scada_equipment_id

                if equipment:
                    move.scada_equipment_id = equipment

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        values = super()._get_move_raw_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            bom_line=bom_line,
        )
        if bom_line and bom_line.scada_equipment_id:
            values['scada_equipment_id'] = bom_line.scada_equipment_id.id
        return values

    def action_confirm(self):
        """Override confirm to ensure SCADA equipment is synced to moves"""
        res = super().action_confirm()
        # After confirmation, ensure all moves have SCADA equipment from BoM
        self._sync_scada_equipment_to_moves()
        return res

    def button_mark_done(self):
        self._scada_normalize_main_finished_moves()
        res = super().button_mark_done()
        oee_model = self.env['scada.equipment.oee']

        for mo in self:
            if mo.state != 'done':
                continue
            equipment = mo.scada_equipment_id or (mo.bom_id.scada_equipment_id if mo.bom_id else False)
            if not equipment:
                continue
            if oee_model.search([('manufacturing_order_id', '=', mo.id)], limit=1):
                continue
            vals = oee_model.prepare_from_mo(mo, equipment)
            oee_model.create(vals)

        return res

    def _scada_normalize_main_finished_moves(self):
        """
        Guard against duplicate unfinished finished-product moves that can
        trigger singleton errors in Odoo core `_post_inventory`.
        """
        for mo in self:
            main_moves = mo.move_finished_ids.filtered(
                lambda m: m.product_id == mo.product_id and m.state not in ('done', 'cancel')
            )
            if len(main_moves) <= 1:
                continue

            keep_move = main_moves.sorted(lambda m: (-(m.product_uom_qty or 0.0), m.id))[0]
            extra_moves = main_moves - keep_move

            # Re-link open move lines to the kept move so existing done/lot data is preserved.
            extra_open_lines = extra_moves.mapped('move_line_ids').filtered(
                lambda ml: ml.state not in ('done', 'cancel')
            )
            if extra_open_lines:
                extra_open_lines.write({'move_id': keep_move.id})

            # Keep total demand consistent after collapsing duplicates.
            keep_move.product_uom_qty = (keep_move.product_uom_qty or 0.0) + sum(
                extra_moves.mapped('product_uom_qty')
            )

            _logger.warning(
                'MO %s has %s unfinished main finished moves. Collapsing into move %s.',
                mo.name, len(main_moves), keep_move.id
            )
            extra_moves._action_cancel()

    def _check_immediate(self):
        """
        Disable core immediate production wizard.
        The wizard auto-fills component consumption from should_consume_qty
        (BoM-theoretical), while SCADA flow must keep manual/middleware actuals.
        """
        return self.browse()

    def _set_qty_producing(self):
        """
        Hybrid behavior:
        - Raw material with manual consumption (> 0) is preserved.
        - Raw material without manual consumption (== 0) is auto-filled by BoM.
        - By-product behavior follows core sync.
        """
        for production in self:
            if production.product_id.tracking == 'serial':
                qty_producing_uom = production.product_uom_id._compute_quantity(
                    production.qty_producing,
                    production.product_id.uom_id,
                    rounding_method='HALF-UP'
                )
                if qty_producing_uom != 1:
                    production.qty_producing = production.product_id.uom_id._compute_quantity(
                        1,
                        production.product_uom_id,
                        rounding_method='HALF-UP'
                    )

            moves_to_sync = (
                production.move_raw_ids |
                production.move_finished_ids.filtered(lambda move: move.product_id != production.product_id)
            )
            for move in moves_to_sync:
                if move._should_bypass_set_qty_producing() or not move.product_uom:
                    continue
                # Preserve manually entered raw material consumption.
                if move.raw_material_production_id and (move.quantity_done or 0.0) > 0.0:
                    continue
                new_qty = float_round(
                    (production.qty_producing - production.qty_produced) * move.unit_factor,
                    precision_rounding=move.product_uom.rounding
                )
                if not move.is_quantity_done_editable:
                    move.move_line_ids.filtered(
                        lambda ml: ml.state not in ('done', 'cancel')
                    ).qty_done = 0
                    move.move_line_ids = move._set_quantity_done_prepare_vals(new_qty)
                else:
                    move.quantity_done = new_qty
        return True
