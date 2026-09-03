# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class StudentStudent(models.Model):
    _inherit = 'student.student'

    # Generated URL uniquely based on current student ID
    kyc_url = fields.Char(
        string='KYC Form Link',
        compute='_compute_kyc_url'
    )

    kyc_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ], string='KYC Status', default='pending', tracking=True)

    def _compute_kyc_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for student in self:
            if student.id:
                # Creates link like: http://localhost:8069/kyc/admission/5
                student.kyc_url = f"{base_url}/kyc/admission/{student.id}"
            else:
                student.kyc_url = False

    def action_open_kyc_url(self):
        self.ensure_one()

        kya = self.env['kyc.form'].search([
            ('student_id', '=', self.id)
        ], limit=1)

        if not kya:
            raise UserError("KYA form is not available for this student.")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kyc.form',
            'view_mode': 'form',
            'res_id': kya.id,
            'target': 'current',
        }