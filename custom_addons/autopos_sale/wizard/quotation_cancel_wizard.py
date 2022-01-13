from odoo import models, fields


class QuotationCancelWizard(models.TransientModel):
    _name = 'autopos.quotation.cancel.wizard'
    quotation_id = fields.Integer('quotation ID')
    quotation_name = fields.Char('quotation Name')

    def do_confirm_cancel(self):
        self.env['autopos.quotation'].browse([self.quotation_id]).sudo().write({'state': 'cancel'})
