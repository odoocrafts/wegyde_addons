# -*- coding: utf-8 -*-
from odoo import models, fields, api

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def action_preview_document(self):
        self.ensure_one()
        wizard = self.env['acca.document.preview'].create({
            'attachment_id': self.id,
        })
        return {
            'name': f"Preview: {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'acca.document.preview',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'dialog_size': 'extra-large'},
        }
