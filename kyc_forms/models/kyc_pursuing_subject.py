# -*- coding: utf-8 -*-
from odoo import models, fields

class KycPursuingSubject(models.Model):
    _name = 'kyc.pursuing.subject'
    _description = 'KYC Form Pursuing Subject & Package'
    _order = 'id asc'

    kyc_form_id = fields.Many2one('kyc.form', string='KYC Form', ondelete='cascade', required=True)
    subject_code = fields.Char(string='Subject Code')
    subject_name = fields.Char(string='Subject Name', required=True)
    package_type = fields.Selection([
        ('Basic', 'Basic'),
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
        ('Offline', 'Offline'),
    ], string='Package', required=True)
