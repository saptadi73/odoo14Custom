from odoo import _, fields, models
from odoo.exceptions import UserError


class DairyBagLocationWizard(models.TransientModel):
    _name = 'dairy.bag.location.wizard'
    _description = 'Wizard Pembuatan Lokasi Tas Petugas'

    person_in_charge = fields.Char(string='Nama Petugas', required=True)
    location_name = fields.Char(string='Nama Lokasi', required=True)
    parent_location_id = fields.Many2one('stock.location', string='Parent Location', required=True, domain=[('usage', '=', 'internal')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)

    @staticmethod
    def _sanitize_code(value):
        cleaned = ''.join(ch for ch in (value or '').upper() if ch.isalnum())
        return cleaned[:10] or 'TAS'

    @api.model
    def default_get(self, fields_list):
        res = super(DairyBagLocationWizard, self).default_get(fields_list)
        company = self.env.company
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        person = ''
        if active_model in ('dairy.treatment.record', 'dairy.medical.stock.transfer') and active_id:
            record = self.env[active_model].browse(active_id)
            person = record.person_in_charge or ''
        source_location = company.dairy_medical_source_location_id or company.dairy_vitamin_source_location_id
        parent_location = source_location.location_id if source_location and source_location.location_id else source_location
        res['person_in_charge'] = person
        res['location_name'] = ('Tas - %s' % person) if person else 'Tas - Petugas'
        res['parent_location_id'] = parent_location.id if parent_location else False
        return res

    def action_create_location(self):
        self.ensure_one()
        if not self.parent_location_id:
            raise UserError(_('Parent location tas petugas wajib diisi.'))
        if not self.person_in_charge:
            raise UserError(_('Nama petugas wajib diisi.'))

        existing = self.env['stock.location'].search([
            ('name', '=', self.location_name),
            ('usage', '=', 'internal'),
            ('company_id', 'in', [False, self.company_id.id]),
        ], limit=1)
        location = existing or self.env['stock.location'].create({
            'name': self.location_name,
            'usage': 'internal',
            'location_id': self.parent_location_id.id,
            'company_id': self.company_id.id,
            'barcode': self._sanitize_code(self.person_in_charge),
        })

        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model in ('dairy.treatment.record', 'dairy.medical.stock.transfer') and active_id:
            record = self.env[active_model].browse(active_id)
            values = {'bag_location_id': location.id}
            if 'person_in_charge' in record._fields and self.person_in_charge:
                values['person_in_charge'] = self.person_in_charge
            record.write(values)

        return {
            'type': 'ir.actions.act_window_close'
        }
