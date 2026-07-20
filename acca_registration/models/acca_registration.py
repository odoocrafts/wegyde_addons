# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccaRegistration(models.Model):
    _name = 'acca.registration'
    _description = 'ACCA Registration'
    _order = 'create_date desc'

    # Zoho Redesign Fields
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    name = fields.Char(string='Student Name', compute='_compute_name', store=True, readonly=False)
    phone = fields.Char(string='Phone Number')
    dob = fields.Date(string='Date of Birth')
    email = fields.Char(string='Email ID', required=True)
    
    image_file = fields.Binary(string='Profile Photo')
    image_filename = fields.Char(string='Photo File Name')
    
    # Address details
    street = fields.Char(string='Street Address')
    street2 = fields.Char(string='Address Line 2')
    city = fields.Char(string='City')
    state = fields.Char(string='State/Region/Province')
    zip_code = fields.Char(string='Postal / Zip Code')
    country = fields.Char(string='Country')
    
    highest_qualification = fields.Text(string='Highest Qualification')
    initial_fees_paid = fields.Boolean(string='Initial Registration Fees Paid')
    # advance_payment = fields.Float(string="Advance Payment")
    address = fields.Text(string='Full Address')

    # Old administrative fields (kept for compatibility)
    wegyde_id = fields.Char(string='WeGyde ID')
    acca_id = fields.Char(string='ACCA ID')

    course_pursuing = fields.Char(string='Course Pursuing')
    educational_qualification = fields.Text(string='Educational Qualification')
    current_subject_level = fields.Char(string='Current Pursuing Subject/Level')
    past_subject_completed = fields.Text(string='Past Subject/Level Completed')
    marks_scored = fields.Text(string='Marks Scored for ACCA Subjects')
    course_purchase_date = fields.Date(string='Course Purchase Date')
    course_expiry_date = fields.Date(string='Course Expiry Date')

    course_extended = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Course Extended?', default='no')
    extension_date = fields.Date(string='Date of Extension')
    free_extension_reason = fields.Text(string='Reason if Free Extension')

    course_freeze = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Course Freeze?', default='no')
    freeze_reason = fields.Text(string='Reason for Course Freeze')
    unfreeze_date = fields.Date(string='Course Unfreeze Date')

    advance_payment = fields.Float(string='Total Advance Payment to be Made')
    contract_file = fields.Binary(string='Signed Contract')
    contract_filename = fields.Char(string='Contract File Name')
    public_url = fields.Char(string='Public Registration URL', compute='_compute_public_url')

    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
        for rec in self:
            rec.public_url = f"{base_url}/acca/register"

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip() or "New Registration"
