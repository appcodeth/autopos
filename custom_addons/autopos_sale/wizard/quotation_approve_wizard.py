from odoo import models, fields


class QuotationApproveWizard(models.TransientModel):
    _name = 'autopos.quotation.approve.wizard'
    quotation_id = fields.Integer('quotation ID')
    quotation_name = fields.Char('quotation Name')

    def do_confirm_approve(self):
        quotation = self.env['autopos.quotation'].browse([self.quotation_id])
        data_dict = {
            'ref_quotation': quotation.name,
            'date_payment': quotation.date_payment,
            'tax_rate': quotation.tax_rate,
            'tax_type': quotation.tax_type,
            'discount_type': quotation.discount_type,
            'discount_rate': quotation.discount_rate,
            'amount_untaxed': quotation.amount_untaxed,
            'amount_tax': quotation.amount_tax,
            'amount_discount': quotation.amount_discount,
            'amount_after_discount': quotation.amount_after_discount,
            'amount_total': quotation.amount_total,
            'remark': quotation.remark,
            'state': 'draft',
            'user_id': quotation.user_id.id,
            'company_id': quotation.company_id.id,
        }

        if quotation.payment_term_id:
            data_dict['payment_term_id'] = quotation.payment_term_id.id
        if quotation.customer_id:
            data_dict['customer_id'] = quotation.customer_id.id
        sale = self.env['autopos.sale'].sudo().create(data_dict)

        for line in quotation.quotation_line:
            item_dict = {
                'sale_id': sale.id,
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
            self.env['autopos.sale_line'].sudo().create(item_dict)

        quotation.sudo().write({'state': 'approve'})
