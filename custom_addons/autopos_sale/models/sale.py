from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from .bahttext import bahttext

TAX_RATE = 7


class Sale(models.Model):
    _name = 'autopos.sale'
    _rec_name = 'name'
    _order = 'name desc'
    name = fields.Char('Name')
    date_order = fields.Date('Date Order', required=True, default=fields.Date.today())
    date_payment = fields.Date('Date Payment')
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
    payment_term_id = fields.Many2one('autopos.payment_term', string='Payment Term')
    customer_id = fields.Many2one('autopos.customer', string='Customer', required=True)
    address = fields.Text('Address', related='customer_id.address')
    phone = fields.Char('Phone', related='customer_id.phone')
    fax = fields.Char('Fax', related='customer_id.fax')
    email = fields.Char('Email', related='customer_id.email')
    tax_id = fields.Char('Tax ID', related='customer_id.tax_id')
    branch = fields.Char('Branch', related='customer_id.branch')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('delivery', 'Delivery'),
        ('invoice', 'Invoice'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    ref_quotation = fields.Char('Ref. Quotation')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    sale_line = fields.One2many('autopos.sale_line', 'sale_id')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('autopos.sale_no') or '-'
        vals['name'] = seq
        return super(Sale, self).create(vals)

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
        return super(Sale, self).copy(default=default)

    @api.onchange('payment_term_id')
    def get_payment_term_id(self):
        pay_date = fields.Datetime.from_string(self.date_order) + \
                   timedelta(days=self.payment_term_id.number_of_day)
        self.date_payment = pay_date

    @api.onchange('sale_line')
    def get_total_amount(self):
        subtotal = 0
        for r in self:
            for item in r.sale_line:
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

    def do_sale_print(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'autopos_sale.sale_form',
            'model': 'autopos.sale',
            'report_type': 'qweb-pdf',
        }

    def do_sale_delivery(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'autopos.po.delivery.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_po_id': self.id,
                'default_po_name': self.name,
            }
        }

    def do_sale_cancel(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'autopos.po.cancel.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_po_id': self.id,
                'default_po_name': self.name,
            }
        }

    def do_sale_close(self):
        self.write({'state': 'close'})

    def do_sale_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('autopos_sale', 'mail_template_sale_form')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'mark_so_as_sent': True,
            'default_model': 'autopos.sale',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'views': [(compose_form_id, 'form')],
        }


class SaleLine(models.Model):
    _name = 'autopos.sale_line'
    sale_id = fields.Many2one('autopos.sale', ondelete='cascade')
    product_id = fields.Many2one('autopos.product', string='Product')
    name = fields.Char('Name')
    description = fields.Text('Description')
    qty = fields.Float('Qty')
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
