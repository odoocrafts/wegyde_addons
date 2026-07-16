from odoo import api, fields, models, _

class Student(models.Model):
    _inherit = "student.student"

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
