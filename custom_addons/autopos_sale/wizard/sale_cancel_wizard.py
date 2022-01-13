from odoo import models, fields


class SaleCancelWizard(models.TransientModel):
    _name = 'autopos.sale.cancel.wizard'
    sale_id = fields.Integer('Sale ID')
    sale_name = fields.Char('Sale Name')

    def do_confirm_cancel(self):
        self.env['autopos.sale'].browse([self.sale_id]).sudo().write({'state': 'cancel'})
