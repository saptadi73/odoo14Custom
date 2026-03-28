
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import datetime, time


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sequence_number_next = fields.Integer('Next Number')
    sequence_id = fields.Many2one('ir.sequence')

    @api.model
    def create(self, vals):
        if vals.get('code'):
            new_seq = self.env['ir.sequence'].create({
                'name': vals['code']+ ' Sequence',
                'implementation': 'no_gap',
                'prefix': vals['code']+'/%(range_year)s/',
                'use_date_range': True,
                'padding': 4,
            })
            date_range = self.env['ir.sequence.date_range'].create({
                'date_from': datetime.strptime('0101'+str(datetime.today().year), '%d%m%Y').date(),
                'date_to': datetime.strptime('3112'+str(datetime.today().year), '%d%m%Y').date(),
                'number_next_actual': vals['sequence_number_next'] if vals.get('sequence_number_next') else 1,
                'sequence_id': new_seq.id
            })
            vals['sequence_id'] = new_seq.id
        result = super(AccountJournal, self).create(vals)
        return result

