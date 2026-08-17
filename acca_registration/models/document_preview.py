# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccaDocumentPreview(models.TransientModel):
    _name = 'acca.document.preview'
    _description = 'ACCA Document In-App Preview'

    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True, ondelete='cascade')
    name = fields.Char(related='attachment_id.name', string='Document Name', readonly=True)
    mimetype = fields.Char(related='attachment_id.mimetype', string='MIME Type', readonly=True)
    file_size = fields.Integer(related='attachment_id.file_size', string='File Size', readonly=True)
    preview_html = fields.Html(compute='_compute_preview_html', string='Document Preview', sanitize=False)

    @api.depends('attachment_id')
    def _compute_preview_html(self):
        for rec in self:
            if not rec.attachment_id:
                rec.preview_html = "<div class='text-muted text-center p-4'>No document selected.</div>"
                continue

            mimetype = (rec.attachment_id.mimetype or '').lower()
            att_id = rec.attachment_id.id
            file_name = rec.attachment_id.name or 'Document'

            if 'pdf' in mimetype:
                rec.preview_html = f"""
                    <div style="width: 100%; height: 78vh; display: flex; flex-direction: column;">
                        <iframe src="/web/content/{att_id}#toolbar=1" 
                                style="width: 100%; height: 100%; border: none; border-radius: 8px; background: #525659;" 
                                frameborder="0">
                        </iframe>
                    </div>
                """
            elif any(t in mimetype for t in ['image', 'jpeg', 'jpg', 'png', 'webp', 'gif', 'svg']):
                rec.preview_html = f"""
                    <div style="text-align: center; max-height: 78vh; overflow: auto; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <img src="/web/image/{att_id}" 
                             style="max-width: 100%; max-height: 72vh; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.15); object-fit: contain;" 
                             alt="{file_name}"/>
                    </div>
                """
            else:
                rec.preview_html = f"""
                    <div class="text-center p-5 bg-light rounded" style="margin: 20px 0;">
                        <i class="fa fa-file-text-o fa-4x text-muted mb-3 d-block"></i>
                        <h4 class="text-dark mb-2">{file_name}</h4>
                        <p class="text-muted mb-4">In-app preview is not available for this file type (<code>{mimetype or 'unknown'}</code>).</p>
                        <a href="/web/content/{att_id}?download=true" class="btn btn-primary btn-lg">
                            <i class="fa fa-download me-2"></i> Download File
                        </a>
                    </div>
                """

    def action_download_file(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.attachment_id.id}?download=true',
            'target': 'self',
        }
