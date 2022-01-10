from odoo import models, fields


class RFQApproveWizard(models.TransientModel):
    _name = 'autopos.rfq.approve.wizard'
    rfq_id = fields.Integer('RFQ ID')
    rfq_name = fields.Char('RFQ Name')

    def do_confirm_approve(self):
        rfq = self.env['autopos.rfq'].browse([self.rfq_id])
        data_dict = {
            'ref_rfq': rfq.name,
            'date_payment': rfq.date_payment,
            'tax_rate': rfq.tax_rate,
            'tax_type': rfq.tax_type,
            'discount_type': rfq.discount_type,
            'discount_rate': rfq.discount_rate,
            'amount_untaxed': rfq.amount_untaxed,
            'amount_tax': rfq.amount_tax,
            'amount_discount': rfq.amount_discount,
            'amount_after_discount': rfq.amount_after_discount,
            'amount_total': rfq.amount_total,
            'remark': rfq.remark,
            'state': 'draft',
            'user_id': rfq.user_id.id,
            'company_id': rfq.company_id.id,
        }

        if rfq.payment_term_id:
            data_dict['payment_term_id'] = rfq.payment_term_id.id
        if rfq.supplier_id:
            data_dict['supplier_id'] = rfq.supplier_id.id
        purchase = self.env['autopos.purchase'].sudo().create(data_dict)

        for line in rfq.rfq_line:
            item_dict = {
                'purchase_id': purchase.id,
                'name': line.name,
                'description': line.description,
                'qty': line.qty,
                'price': line.price,
                'tax': line.tax,
                'discount': line.discount,
                'amount': line.amount,
            }
            if line.product_id:
                item_dict['product_id'] = line.product_id.id
            if line.uom_id:
                item_dict['uom_id'] = line.uom_id.id
            self.env['autopos.purchase_line'].sudo().create(item_dict)

        rfq.sudo().write({'state': 'approve'})
