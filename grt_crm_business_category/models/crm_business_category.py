from odoo import fields, models


class CrmBusinessCategory(models.Model):
    _name = "crm.business.category"
    _description = "CRM Business Category"
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

    _sql_constraints = [
        (
            "crm_business_category_name_company_uniq",
            "unique(name, company_id)",
            "Business category name must be unique per company.",
        ),
    ]
