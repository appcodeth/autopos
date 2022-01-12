from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from .bahttext import bahttext

TAX_RATE = 7


class Receive(models.Model):
    _name = 'autopos.receive'
    _rec_name = 'name'
    _order = 'name desc'
    name = fields.Char('Name')
    date_receive = fields.Date('Date Receive', required=True, default=fields.Date.today())
    purchase_id = fields.Many2one('autopos.purchase', string='Purchase', required=True)
    supplier_id = fields.Many2one('autopos.supplier', related='purchase_id.supplier_id', string='Supplier')
    tax_rate = fields.Float('Tax Rate', default=7)
    tax_type = fields.Selection([
        ('include', 'Include'),
        ('exclude', 'Exclude'),
    ], string='Tax Type', default='exclude')
    discount_type = fields.Selection([
        ('no', 'No Discount'),
        ('percent', 'Percent'),
        ('amount', 'Amount'),
    ], default='no', string='Discount Type')
    discount_rate = fields.Float(string='Discount %')
    amount_untaxed = fields.Float('Subtotal', readonly=True, store=True)
    amount_tax = fields.Float('Taxes', readonly=True, store=True)
    amount_discount = fields.Float('Discount Amount')
    amount_after_discount = fields.Float('Price after discount', readonly=True, store=True)
    amount_total = fields.Float('Total Amount', default=0, readonly=True, store=True)
    remark = fields.Text('Remark')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    receive_line = fields.One2many('autopos.receive_line', 'receive_id')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('autopos.receive_no') or '-'
        vals['name'] = seq
        return super(Receive, self).create(vals)

    @api.model
    def get_baht_text(self):
        return bahttext(self.amount_total)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'amount_untaxed': 0,
            'amount_tax': 0,
            'amount_discount': 0,
            'amount_after_discount': 0,
            'amount_total': 0,
            'state': 'draft',
        })
        return super(Receive, self).copy(default=default)

    @api.onchange('receive_line')
    def get_total_amount(self):
        subtotal = 0
        for r in self:
            for item in r.receive_line:
                subtotal += item.amount

        discount = 0
        if self.discount_type == 'percent':
            discount = (subtotal * self.discount_rate / 100)
        elif self.discount_type == 'amount':
            discount = self.amount_discount

        price_after_discount = subtotal - discount

        self.tax_rate = TAX_RATE
        self.amount_tax = 0
        self.amount_untaxed = subtotal
        self.amount_after_discount = price_after_discount
        self.amount_total = price_after_discount

        if self.tax_type == 'include':
            amount_exclude_tax = (price_after_discount * 100) / (100 + TAX_RATE)
            self.amount_tax = price_after_discount - amount_exclude_tax
            self.amount_total = price_after_discount
        elif self.tax_type == 'exclude':
            self.amount_tax = (price_after_discount * TAX_RATE) / 100
            self.amount_total = price_after_discount + self.amount_tax

    @api.onchange('discount_type')
    def change_discount_type(self):
        self.discount_rate = 0
        self.amount_discount = 0
        self.get_total_amount()

    @api.onchange('discount_rate')
    def change_discount_rate(self):
        if self.discount_type == 'percent':
            if self.discount_rate or self.discount_rate == 0:
                self.get_total_amount()
            else:
                raise exceptions.ValidationError('Please enter a valid percent')

    @api.onchange('amount_discount')
    def change_amount_discount(self):
        if self.discount_type == 'amount':
            if self.amount_discount or self.amount_discount == 0:
                self.get_total_amount()
            else:
                raise exceptions.ValidationError('Please enter a valid amount')

    @api.onchange('tax_type')
    def get_tax_type_change(self):
        self.get_total_amount()

    def do_receive_approve(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'autopos.receive.approve.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_rcv_id': self.id,
                'default_rcv_name': self.name,
            }
        }

    def do_receive_cancel(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'autopos.receive.cancel.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_rcv_id': self.id,
                'default_rcv_name': self.name,
            }
        }

    def do_receive_print(self):
        return {
            'type': 'ir.actions.report',
            'report_name': 'autopos_inventory.receive_form',
            'model': 'autopos.receive',
            'report_type': 'qweb-pdf',
        }

    def do_receive_close(self):
        self.write({'state': 'close'})


class ReceiveLine(models.Model):
    _name = 'autopos.receive_line'
    receive_id = fields.Many2one('autopos.receive', ondelete='cascade')
    product_id = fields.Many2one('autopos.product', string='Product')
    name = fields.Char('Name')
    description = fields.Text('Description')
    qty = fields.Float('Qty')
    qty_receive = fields.Float('Qty Receive')
    uom_id = fields.Many2one('autopos.uom', string='Uom')
    price = fields.Float('Unit Price')
    tax = fields.Float('Tax')
    discount = fields.Float('Discount')
    amount = fields.Float('Amount', readonly=True, store=True)

    @api.onchange('product_id')
    def get_product_change(self):
        if not self.product_id:
            return
        self.uom_id = self.product_id.uom_id
        self.price = self.product_id.cost_price
        self.name = '[{0}] {1}'.format(self.product_id.code, self.product_id.name)
        if not self.qty:
            self.qty = 1
        self.amount = self.price * self.qty

    @api.onchange('price', 'qty')
    def price_qty_change(self):
        if not self.qty:
            self.qty = 1
        if not self.price:
            self.price = 0
