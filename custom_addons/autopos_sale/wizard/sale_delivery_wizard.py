from odoo import models, fields
from datetime import datetime


class SaleDeliveryWizard(models.TransientModel):
    _name = 'autopos.sale.delivery.wizard'
    sale_id = fields.Integer('Sale ID')
    sale_name = fields.Char('Sale Name')

    def do_confirm_delivery(self):
        sale = self.env['autopos.sale'].browse([self.sale_id])

        total_qty = 0
        total_amount = 0
        for item in sale.sale_line:
            if item.product_id.type == 'product':
                total_qty += item.qty
                total_amount += item.amount

        if total_qty > 0:
            delivery = self.env['autopos.delivery'].sudo().create({
                'sale_id': sale.id,
                'customer_id': sale.customer_id.id,
                'date_rcv': datetime.now(),
                'discount_rate': sale.discount_rate,
                'amount_qty': total_qty,
                'amount_total': total_amount,
                'state': 'draft',
            })

            for item in sale.sale_line:
                if item.product_id.type == 'product':
                    self.env['autopos.delivery_line'].sudo().create({
                        'rcv_id': delivery.id,
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'name': item.name,
                        'qty': item.qty,
                        'price': item.price,
                        'amount': item.amount,
                    })

        sale.sudo().write({'state': 'delivery'})
