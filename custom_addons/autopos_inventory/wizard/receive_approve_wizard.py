from odoo import models, fields, exceptions, _
from datetime import datetime


class ReceiveApproveWizard(models.TransientModel):
    _name = 'autopos.receive.approve.wizard'
    rcv_id = fields.Integer('Receive ID')
    rcv_name = fields.Char('Receive Name')

    def do_confirm_approve(self):
        receive = self.env['autopos.receive'].browse([self.rcv_id])

        for line in receive.receive_line:
            if not line.uom_id:
                raise exceptions.ValidationError(_('Please select uom in receive line'))
            if not line.price:
                raise exceptions.ValidationError(_('Please enter product price in receive line'))

        for line in receive.receive_line:
            if line.product_id.type == 'service':
                continue

            base_uom = line.product_id.uom_id
            receive_uom = line.uom_id
            ratio = base_uom.ratio or 1
            if base_uom.id != receive_uom.id:
                if receive_uom.type == 'bigger':
                    ratio = base_uom.ratio * receive_uom.ratio
                elif receive_uom.type == 'smaller':
                    ratio = base_uom.ratio / receive_uom.ratio
            new_qty = line.qty * ratio
            last_purchase = datetime.now()

            product = self.env['autopos.product'].browse([line.product_id.id])
            product.sudo().write({
                'last_purchase_date': last_purchase,
                'stock_qty': product.stock_qty + new_qty,
            })

            self.env['autopos.stock_move'].sudo().create({
                'name': line.product_id.name,
                'doc_id': self.rcv_id,
                'doc_name': self.rcv_name,
                'doc_type': 'receive',
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
        receive.sudo().write({'state': 'complete'})
