from odoo import models, fields
from datetime import datetime


class POReceiveWizard(models.TransientModel):
    _name = 'autopos.po.receive.wizard'
    po_id = fields.Integer('PO ID')
    po_name = fields.Char('PO Name')

    def do_confirm_receive(self):
        purchase = self.env['autopos.purchase'].browse([self.po_id])

        total_qty = 0
        total_amount = 0
        for item in purchase.purchase_line:
            if item.product_id.type == 'product':
                total_qty += item.qty
                total_amount += item.amount

        if total_qty > 0:
            receive = self.env['autopos.receive'].sudo().create({
                'po_id': purchase.id,
                'supplier_id': purchase.supplier_id.id,
                'date_rcv': datetime.now(),
                'discount_rate': purchase.discount_rate,
                'amount_qty': total_qty,
                'amount_total': total_amount,
                'state': 'draft',
            })

            for item in purchase.purchase_line:
                if item.product_id.type == 'product':
                    self.env['autopos.receive_line'].sudo().create({
                        'rcv_id': receive.id,
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'name': item.name,
                        'qty': item.qty,
                        'price': item.price,
                        'amount': item.amount,
                    })

        purchase.sudo().write({'state': 'receive'})
