from odoo import models, fields, api


class PaymentTerm(models.Model):
    _name = 'autopos.payment_term'
    name = fields.Char('Name', required=True)
    number_of_day = fields.Integer('No. of Days')
    description = fields.Text('Description')
