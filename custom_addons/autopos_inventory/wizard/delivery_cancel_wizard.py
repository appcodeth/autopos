from odoo import models, fields


class DeliveryCancelWizard(models.TransientModel):
    _name = 'autopos.delivery.cancel.wizard'
    do_id = fields.Integer('Delivery ID')
    do_name = fields.Char('Delivery Name')

    def do_confirm_cancel(self):
        self.env['autopos.delivery'].browse([self.do_id]).sudo().write({'state': 'cancel'})
