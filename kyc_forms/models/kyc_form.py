# -*- coding: utf-8 -*-
from odoo import models, fields, api

class KycForm(models.Model):
    _name = 'kyc.form'
    _description = 'WeGyde Admission - KYC Form'
    _order = 'create_date desc'

    name = fields.Char(string='Student Name', compute='_compute_name', store=True)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    phone = fields.Char(string='Mobile Number (WhatsApp)', required=True)
    email = fields.Char(string='Email Address', required=True)
    dob = fields.Date(string='Date of Birth', required=True)
    
    image_file = fields.Binary(string='KYC Image Photo', attachment=True)
    image_filename = fields.Char(string='Image Filename')
    
    highest_qualification = fields.Selection([
        ('12th Pass', '12th Pass'),
        ('Graduation (B.Com, BBA etc)', 'Graduation (B.Com, BBA etc)'),
        ('CA Inter', 'CA Inter'),
        ('CA', 'CA'),
        ('Other', 'Other'),
    ], string='Highest Qualification', required=True)
    
    street = fields.Char(string='Street Address', required=True)
    street2 = fields.Char(string='Address Line 2')
    city = fields.Char(string='City', required=True)
    state = fields.Char(string='State / Region / Province', required=True)
    zip_code = fields.Char(string='Postal / Zip Code', required=True)
    country = fields.Char(string='Country', required=True)
    
    acca_reg_number = fields.Char(string='ACCA Registration Number', required=True)
    languages = fields.Char(string='Languages Known')
    
    subject_line_ids = fields.One2many(
        'kyc.pursuing.subject', 
        'kyc_form_id', 
        string='Pursuing Subjects & Packages'
    )
    
    referral_source = fields.Selection([
        ('Linkedin', 'Linkedin'),
        ('Instagram & Facebook', 'Instagram & Facebook'),
        ('Youtube', 'Youtube'),
        ("Friend's Referral", "Friend's Referral"),
        ('Google Search', 'Google Search'),
        ('Other', 'Other'),
    ], string='How did you get to know us?', required=True)

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            parts = [p.strip() for p in [rec.first_name, rec.last_name] if p and p.strip()]
            rec.name = " ".join(parts) if parts else "New KYC Submission"
