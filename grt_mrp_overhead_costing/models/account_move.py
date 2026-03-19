from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    mrp_overhead_type_id = fields.Many2one(
        "mrp.overhead.type",
        string="MRP Overhead Type",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    mrp_overhead_period_id = fields.Many2one(
        "mrp.overhead.period",
        string="MRP Overhead Period",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )

    @api.constrains("company_id", "mrp_overhead_type_id", "mrp_overhead_period_id")
    def _check_mrp_overhead_company(self):
        for move in self:
            if move.mrp_overhead_type_id and move.mrp_overhead_type_id.company_id != move.company_id:
                raise ValidationError(
                    _("Journal Entry '%s' uses an overhead type from another company.") % move.display_name
                )
            if move.mrp_overhead_period_id and move.mrp_overhead_period_id.company_id != move.company_id:
                raise ValidationError(
                    _("Journal Entry '%s' uses an overhead period from another company.") % move.display_name
                )

    def action_post(self):
        result = super().action_post()
        for move in self:
            if move.mrp_overhead_type_id:
                move.line_ids.filtered(
                    lambda line: not line.display_type
                    and line.account_id.internal_type not in ("receivable", "payable", "liquidity")
                    and not line.mrp_overhead_period_line_id
                ).write(
                    {
                        "mrp_overhead_type_id": move.mrp_overhead_type_id.id,
                        "mrp_overhead_period_id": move.mrp_overhead_period_id.id,
                    }
                )

            period = move.mrp_overhead_period_id.filtered(lambda item: item.adjustment_move_id == move)
            if period:
                period.action_sync_posted_adjustment_valuation()
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    mrp_overhead_type_id = fields.Many2one(
        "mrp.overhead.type",
        string="MRP Overhead Type",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    mrp_overhead_period_id = fields.Many2one(
        "mrp.overhead.period",
        string="MRP Overhead Period",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    mrp_overhead_period_line_id = fields.Many2one(
        "mrp.overhead.period.line",
        string="MRP Overhead Period Line",
        copy=False,
        ondelete="set null",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move_id = vals.get("move_id")
            if not move_id:
                continue
            move = self.env["account.move"].browse(move_id)
            if (
                move
                and move.mrp_overhead_type_id
                and not vals.get("mrp_overhead_type_id")
                and not vals.get("display_type")
            ):
                vals["mrp_overhead_type_id"] = move.mrp_overhead_type_id.id
            if (
                move
                and move.mrp_overhead_period_id
                and not vals.get("mrp_overhead_period_id")
                and not vals.get("display_type")
            ):
                vals["mrp_overhead_period_id"] = move.mrp_overhead_period_id.id
        return super().create(vals_list)
