from odoo import models, fields


class POCancelWizard(models.TransientModel):
    _name = 'autopos.po.cancel.wizard'
    po_id = fields.Integer('PO ID')
    po_name = fields.Char('PO Name')

    def do_confirm_cancel(self):
        self.env['autopos.purchase'].browse([self.po_id]).sudo().write({'state': 'cancel'})
