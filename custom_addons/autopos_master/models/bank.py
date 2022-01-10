from odoo import models, fields, api


class Bank(models.Model):
    _name = 'autopos.bank'
    _rec_name = 'name'
    name = fields.Char('Name', required=True)
    short_name = fields.Char('Short Name')

    @api.depends('name')
    def name_get(self):
        res = []
        for record in self:
            name = '[{0}] {1}'.format(record.short_name, record.name)
            res.append((record.id, name))
        return res


class BankAccount(models.Model):
    _name = 'autopos.bank_account'
    _rec_name = 'account_name'
    account_name = fields.Char('Account Name', required=True)
    account_no = fields.Char('Account No')
    bank_id = fields.Many2one('autopos.bank', string='Bank Name')
    bank_branch = fields.Char('Bank Branch')
    bank_type = fields.Selection([('saving', 'Saving'), ('current', 'Current')], string='Bank Type')
