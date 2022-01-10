from odoo import models, fields, api


class Category(models.Model):
    _name = 'autopos.category'
    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one('autopos.category', string='Parent')
    type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service'),
    ], string='Type', default='product')
    costing_method = fields.Selection([
        ('standard', 'Standard'),
        ('average', 'Average'),
    ], string='Costing Method', default='standard')
