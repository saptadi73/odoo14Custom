from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        default=lambda self: self.env["business.category.mixin"]._default_business_category_id(),
        ondelete="restrict",
        index=True,
        help="Shared business category for operational products. System-generated products may leave this empty.",
    )

    @api.onchange("business_category_id")
    def _onchange_business_category_id_company(self):
        for template in self:
            if template.business_category_id and template.business_category_id.company_id:
                template.company_id = template.business_category_id.company_id

    @api.onchange("company_id")
    def _onchange_company_id_business_category(self):
        for template in self:
            if template.business_category_id and template.business_category_id.company_id != template.company_id:
                template.business_category_id = False

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._prepare_business_category_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        vals = self._prepare_business_category_vals(vals)
        return super().write(vals)

    def _prepare_business_category_vals(self, vals):
        vals = dict(vals)
        if vals.get("business_category_id") and not vals.get("company_id"):
            category = self.env["crm.business.category"].browse(vals["business_category_id"])
            if category.company_id:
                vals["company_id"] = category.company_id.id
        return vals

    @api.constrains("company_id", "business_category_id")
    def _check_business_category_company(self):
        for template in self:
            if not template.company_id or not template.business_category_id:
                continue
            if template.business_category_id.company_id != template.company_id:
                raise ValidationError(
                    _(
                        "Product '%s' must use a Business Category from company '%s'."
                    )
                    % (template.display_name, template.company_id.name)
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    business_category_id = fields.Many2one(
        "crm.business.category",
        string="Business Category",
        related="product_tmpl_id.business_category_id",
        store=True,
        readonly=True,
    )
