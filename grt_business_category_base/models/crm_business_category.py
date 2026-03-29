from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmBusinessCategory(models.Model):
    _name = "crm.business.category"
    _description = "Business Category"
    _order = "name"

    def init(self):
        self._cr.execute(
            """
            UPDATE crm_business_category
               SET company_id = %s
             WHERE company_id IS NULL
            """,
            [self.env.ref("base.main_company").id],
        )

    name = fields.Char(required=True)
    code = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    description = fields.Text()
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        domain="[('company_id', '=', company_id)]",
        ondelete="restrict",
        help="Shared default analytic account used by modules that reference this business category.",
    )

    _sql_constraints = [
        (
            "crm_business_category_name_company_uniq",
            "unique(name, company_id)",
            "Business category name must be unique per company.",
        ),
    ]

    @api.constrains("company_id", "analytic_account_id")
    def _check_analytic_account_company(self):
        for category in self:
            if not category.analytic_account_id or not category.company_id:
                continue
            if category.analytic_account_id.company_id != category.company_id:
                raise ValidationError(
                    _(
                        "Business Category '%s' must use an Analytic Account from company '%s'."
                    )
                    % (category.name, category.company_id.name)
                )
