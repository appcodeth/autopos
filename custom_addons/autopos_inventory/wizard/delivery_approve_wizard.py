from odoo import models, fields, exceptions, _
from datetime import datetime


class DeliveryApproveWizard(models.TransientModel):
    _name = 'autopos.delivery.approve.wizard'
    do_id = fields.Integer('Delivery ID')
    do_name = fields.Char('Delivery Name')

    def do_confirm_approve(self):
        delivery = self.env['autopos.delivery'].browse([self.do_id])

        for line in delivery.delivery_line:
            if not line.uom_id:
                raise exceptions.ValidationError(_('Please select uom in delivery line'))
            if not line.price:
                raise exceptions.ValidationError(_('Please enter product price in delivery line'))

        for line in delivery.delivery_line:
            if line.product_id.type == 'service':
                continue

            base_uom = line.product_id.uom_id
            delivery_uom = line.uom_id
            ratio = base_uom.ratio or 1
            if base_uom.id != delivery_uom.id:
                if delivery_uom.type == 'bigger':
                    ratio = base_uom.ratio * delivery_uom.ratio
                elif delivery_uom.type == 'smaller':
                    ratio = base_uom.ratio / delivery_uom.ratio
            new_qty = line.qty * ratio
            last_purchase = datetime.now()

            product = self.env['autopos.product'].browse([line.product_id.id])
            product.sudo().write({
                'last_purchase_date': last_purchase,
                'stock_qty': product.stock_qty + new_qty,
            })

            self.env['autopos.stock_move'].sudo().create({
                'name': line.product_id.name,
                'doc_id': self.do_id,
                'doc_name': self.do_name,
                'doc_type': 'delivery',
                'product_id': line.product_id.id,
                'product_code': line.product_id.code,
                'user_id': self.env.user.id,
                'qty': new_qty,
                'uom_id': line.product_id.uom_id.id,
                'purchase_qty': line.qty,
                'purchase_uom_id': line.uom_id.id,
                'amount': line.price,
                'move_type': 'in',
                'move_date': datetime.now(),
            })
        delivery.sudo().write({'state': 'complete'})
