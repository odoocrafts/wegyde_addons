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
    past_subject_ids = fields.One2many(
        'student.past.subject',
        'student_id',
        string='Past Subjects'
    )
    course_purchase_date = fields.Date(string='Course Purchase Date')
    course_expiry_date = fields.Date(string='Course Expiry Date')
    branch = fields.Many2one(
        "student.branch",
        string="Branch",
        required=False,
    )
    has_pending_amount = fields.Boolean(
        string="Fee Pending",
        compute="_compute_has_pending_amount",
        store=True,
    )

    @api.depends("pending_amount")
    def _compute_has_pending_amount(self):
        for rec in self:
            rec.has_pending_amount = rec.pending_amount > 0

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

class StudentPastSubject(models.Model):
    _name = 'student.past.subject'
    _description = 'Student Past Subject'

    student_id = fields.Many2one(
        'student.student',
        string='Student',
        ondelete='cascade'
    )
    past_subject_completed = fields.Char(
        string='Past Subject / Level Completed',

    )
    marks_scored = fields.Float(
        string='Marks Scored for ACCA Subjects'
    )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(
        related='type',
        default='service',
        readonly=False,
    )