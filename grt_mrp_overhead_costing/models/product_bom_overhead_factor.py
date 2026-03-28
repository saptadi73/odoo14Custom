from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    overhead_electricity_factor_default = fields.Float(
        string="Default Electricity Factor",
        digits=(16, 4),
        default=1.0,
        help="Faktor listrik default saat membuat MO dari produk ini.",
    )
    overhead_labor_factor_default = fields.Float(
        string="Default Labor Factor",
        digits=(16, 4),
        default=1.0,
        help="Faktor SDM default saat membuat MO dari produk ini.",
    )

    @api.constrains("overhead_electricity_factor_default", "overhead_labor_factor_default")
    def _check_overhead_factor_defaults(self):
        for template in self:
            if template.overhead_electricity_factor_default < 0:
                raise ValidationError(_("Default Electricity Factor tidak boleh negatif."))
            if template.overhead_labor_factor_default < 0:
                raise ValidationError(_("Default Labor Factor tidak boleh negatif."))


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    overhead_electricity_factor_default = fields.Float(
        string="Default Electricity Factor",
        digits=(16, 4),
        default=1.0,
        help="Override faktor listrik default ketika MO memakai BoM ini.",
    )
    overhead_labor_factor_default = fields.Float(
        string="Default Labor Factor",
        digits=(16, 4),
        default=1.0,
        help="Override faktor SDM default ketika MO memakai BoM ini.",
    )

    @api.constrains("overhead_electricity_factor_default", "overhead_labor_factor_default")
    def _check_overhead_factor_defaults(self):
        for bom in self:
            if bom.overhead_electricity_factor_default < 0:
                raise ValidationError(_("Default Electricity Factor pada BoM tidak boleh negatif."))
            if bom.overhead_labor_factor_default < 0:
                raise ValidationError(_("Default Labor Factor pada BoM tidak boleh negatif."))