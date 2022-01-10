from odoo import models, fields, api, _


class Product(models.Model):
    _name = 'autopos.product'
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, unique=True)
    barcode = fields.Char('Barcode', unique=True)
    lot_no = fields.Char('Lot No')
    serial_no = fields.Char('Serial No')
    image = fields.Binary('Image')
    type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service'),
    ], default='product', string='Type')
    category_id = fields.Many2one('autopos.category', string='Category')
    uom_id = fields.Many2one('autopos.uom', string='Uom')
    stock_qty = fields.Float('Stock Qty', default=0)
    reorder_qty = fields.Float('Reorder Qty', default=0)
    unit_price = fields.Float('Unit Price')
    cost_price = fields.Float('Cost Price')
    description = fields.Text('Description')
    last_purchase_date = fields.Date('Last Purchase Date', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('field_code', 'unique (code,company_id)', _('Product code is existed')),
        ('field_barcode', 'unique (barcode,company_id)', _('Product barcode is existed')),
    ]

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = '[' + str(record.code) + ']' + ' ' + record.name
    #         result.append((record.id, name))
    #     return result
