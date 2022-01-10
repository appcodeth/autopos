from odoo import models, fields, api


class UomCategory(models.Model):
    _name = 'autopos.uom_category'
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class Uom(models.Model):
    _name = 'autopos.uom'
    name = fields.Char('Name', required=True)
    name_en = fields.Char('Name English')
    type = fields.Selection([
        ('smaller', 'Smaller than the reference'),
        ('equal', 'Equal the reference'),
        ('bigger', 'Bigger than the reference'),
    ], default='equal', string='Reference Type')
    ratio = fields.Float('Ratio', default=1)
    category_id = fields.Many2one('autopos.uom_category', string='Uom Category')
