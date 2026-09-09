from odoo import api, fields, models, _


class Student(models.Model):
    _inherit = "student.student"

    wegyde_id = fields.Char(string='WeGyde ID')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    # Automatically computed and stored in database
    name = fields.Char(
        string='Student Name',
        compute='_compute_name',
        store=True,
        readonly=False,
        required=False,
        precompute=True  # Ensures computation happens BEFORE database insert during imports
    )

    # 1. LIVE COMPUTE (Works in UI & whenever fields change)
    @api.onchange('first_name', 'last_name')
    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            names = [part.strip() for part in [rec.first_name, rec.last_name] if part]
            rec.name = " ".join(names) if names else (rec.name or "New Student")

    # 2. CSV / EXCEL IMPORT & ORM CREATION SUPPORT
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            first = vals.get('first_name', '')
            last = vals.get('last_name', '')
            # If importing without 'name' column, construct it automatically
            if (first or last) and not vals.get('name'):
                vals['name'] = f"{first or ''} {last or ''}".strip()
        return super(Student, self).create(vals_list)

    # 3. CSV UPDATE & MASS WRITE SUPPORT
    def write(self, vals):
        res = super(Student, self).write(vals)
        # If first_name or last_name is updated during import/write, re-sync name
        if 'first_name' in vals or 'last_name' in vals:
            for rec in self:
                if not vals.get('name'):
                    new_name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()
                    if new_name and rec.name != new_name:
                        # Use update to avoid infinite recursion
                        rec.write({'name': new_name})
        return res

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
    # paper_id = fields.Many2one('course.paper', string='Paper')
    # language_id = fields.Many2one('course.language', string='Language')
    # plan_id = fields.Many2one('course.plan', string='Plan')

    @api.depends("pending_amount")
    def _compute_has_pending_amount(self):
        for rec in self:
            print('hi')
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

    is_acca = fields.Boolean(
        string='Is ACCA Course',
        compute='_compute_is_acca',
        store=True
    )

    @api.depends('course_id')
    def _compute_is_acca(self):
        for rec in self:
            is_acca_val = False
            if rec.course_id:
                # Check product variant
                if hasattr(rec.course_id, 'is_acca') and rec.course_id.is_acca:
                    is_acca_val = True
                # Check product template
                elif hasattr(rec.course_id.product_tmpl_id, 'is_acca') and rec.course_id.product_tmpl_id.is_acca:
                    is_acca_val = True
                # Fallback: check if 'ACCA' is in product name
                elif 'ACCA' in (rec.course_id.name or '').upper():
                    is_acca_val = True
            rec.is_acca = is_acca_val

    paper_ids = fields.Many2many('acca.paper', string='Selected Papers')
    language_ids = fields.Many2many('acca.language', string='Selected Languages')
    plan_ids = fields.Many2many('acca.plan', string='Selected Plans')
    paper_line_ids = fields.One2many(
        'student.paper.line',
        'student_id',
        string='Enrolled Papers'
    )
    course_fee = fields.Float(
        string='Course Fee',
        compute='_compute_course_fee',
        store=True,
        readonly=False
    )

    @api.onchange('paper_line_ids', 'course_id', 'is_acca')
    @api.depends('is_acca', 'course_id', 'paper_line_ids.fee_amount')
    def _compute_course_fee(self):
        print('--> Course Fee Triggered on Parent')
        for student in self:
            if not student.is_acca:
                student.course_fee = student.course_id.list_price if student.course_id else 0.0
                continue
            # Sum of all lines in the table
            student.course_fee = sum(line.fee_amount for line in student.paper_line_ids)
            print(f'--> Student Total Course Fee: {student.course_fee}')

    # @api.onchange('course_id', 'is_acca', 'paper_ids', 'language_ids', 'plan_ids')
    # @api.depends('course_id', 'is_acca', 'paper_ids', 'language_ids', 'plan_ids')
    # def _compute_course_fee(self):
    #     for student in self:
    #         # 1. Non-ACCA Course: Take standard list_price
    #         if not student.is_acca:
    #             student.course_fee = student.course_id.list_price if student.course_id else 0.0
    #             continue
    #         # 2. ACCA Course: If any selection is missing, reset fee to 0
    #         if not (student.paper_ids and student.language_ids and student.plan_ids):
    #             student.course_fee = 0.0
    #             continue
    #         total = 0.0
    #
    #         # Helper to get real integer DB ID (prevents NewId bugs)
    #         def get_real_id(record):
    #             orig_id = record._origin.id if hasattr(record, '_origin') else record.id
    #             print(orig_id, 'orig')
    #             return orig_id if isinstance(orig_id, int) else (record.id if isinstance(record.id, int) else False)
    #
    #         # Loop through all selected combinations
    #         for paper in student.paper_ids:
    #             paper_id = get_real_id(paper)
    #             if not paper_id:
    #                 continue
    #             for lang in student.language_ids:
    #                 lang_id = get_real_id(lang)
    #                 if not lang_id:
    #                     continue
    #                 for plan in student.plan_ids:
    #                     plan_id = get_real_id(plan)
    #                     if not plan_id:
    #                         continue
    #                     # Search pre-set price in ACCA Fee Matrix
    #                     fee_rule = self.env['acca.fee.matrix'].search([
    #                         ('paper_id', '=', paper_id),
    #                         ('language_id', '=', lang_id),
    #                         ('plan_id', '=', plan_id),
    #                     ], limit=1)
    #                     if fee_rule:
    #                         total += fee_rule.price
    #                         print(
    #                             f"[ACCA Fee] Found Match: {paper.name} + {lang.name} + {plan.name} = {fee_rule.price}")
    #                     else:
    #                         print(
    #                             f"[ACCA Fee] NO Rule found in matrix for: {paper.name} (ID: {paper_id}), {lang.name} (ID: {lang_id}), {plan.name} (ID: {plan_id})")
    #         print(f"[ACCA Fee] Final Total Fee Calculated: {total}")
    #         student.course_fee = total
    # @api.onchange('plan_ids')
    # @api.depends('plan_ids')
    # def _compute_course_fee(self):
    #     for student in self:
    #         # If not ACCA or plan is not chosen yet, do not calculate from matrix
    #         if not student.is_acca:
    #             student.course_fee = student.course_id.list_price if student.course_id else 0.0
    #             continue
    #
    #         # Gate: ONLY compute if plan_ids is set
    #         if not (student.plan_ids and student.paper_ids and student.language_ids):
    #             student.course_fee = 0.0
    #             continue
    #
    #         total = 0.0
    #
    #         def get_real_id(record):
    #             orig_id = record._origin.id if hasattr(record, '_origin') else record.id
    #             return orig_id if isinstance(orig_id, int) else (record.id if isinstance(record.id, int) else False)
    #
    #         for paper in student.paper_ids:
    #             paper_id = get_real_id(paper)
    #             if not paper_id:
    #                 continue
    #             for lang in student.language_ids:
    #                 lang_id = get_real_id(lang)
    #                 if not lang_id:
    #                     continue
    #                 for plan in student.plan_ids:
    #                     plan_id = get_real_id(plan)
    #                     if not plan_id:
    #                         continue
    #                     fee_rule = self.env['acca.fee.matrix'].search([
    #                         ('paper_id', '=', paper_id),
    #                         ('language_id', '=', lang_id),
    #                         ('plan_id', '=', plan_id),
    #                     ], limit=1)
    #                     if fee_rule:
    #                         total += fee_rule.price
    #
    #         student.course_fee = total


class StudentPastSubjectCourse(models.Model):
    _name = 'student.past.subject.course'
    _description = 'Past Subject / Course'

    name = fields.Char(
        string='Course / Level',
        required=True
    )


class StudentPastSubject(models.Model):
    _name = 'student.past.subject'
    _description = 'Student Past Subject'

    student_id = fields.Many2one(
        'student.student',
        string='Student',
        ondelete='cascade'
    )
    past_subject_completed = fields.Many2one(
        'student.past.subject.course',
        string='Past Subject / Level Completed',
        ondelete='set null'
    )
    year = fields.Integer(
        string='Year'
    )
    marks_scored = fields.Float(
        string='Marks Scored for ACCA Subjects'
    )

class StudentPaperLine(models.Model):
    _name = 'student.paper.line'
    _description = 'Student Enrolled Paper Line'
    student_id = fields.Many2one('student.student', string='Student', ondelete='cascade', required=True)
    paper_id = fields.Many2one('acca.paper', string='Paper', required=True)
    language_id = fields.Many2one('acca.language', string='Language', required=True)
    plan_id = fields.Many2one('acca.plan', string='Plan', required=True)
    fee_amount = fields.Float(
        string='Fee Amount',
        compute='_compute_fee_amount',
        store=True,
        readonly=False
    )
    # -------------------------------------------------------------
    # CALCULATE FEE ONLY WHEN PLAN IS SELECTED / CHANGED
    # -------------------------------------------------------------
    @api.onchange('paper_id', 'language_id', 'plan_id')
    @api.depends('paper_id', 'language_id', 'plan_id')
    def _compute_fee_amount(self):
        for line in self:
            if not (line.paper_id and line.language_id and line.plan_id):
                line.fee_amount = 0.0
                continue
            paper_id = line.paper_id._origin.id or line.paper_id.id
            lang_id = line.language_id._origin.id or line.language_id.id
            plan_id = line.plan_id._origin.id or line.plan_id.id
            fee_rule = self.env['acca.fee.matrix'].search([
                ('paper_id', '=', paper_id),
                ('language_id', '=', lang_id),
                ('plan_id', '=', plan_id),
            ], limit=1)
            line.fee_amount = fee_rule.price if fee_rule else 0.0
            print(f'--> Row Fee: {line.paper_id.name} ({line.plan_id.name}) = {line.fee_amount}')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(
        related='type',
        default='service',
        readonly=False,
    )

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_acca = fields.Boolean(
        string='Is ACCA Course?',
        help='Check this if this course follows the ACCA Paper/Language/Plan fee structure.'
    )


class CoursePaper(models.Model):
    _name = 'course.paper'
    _description = 'Course Paper'
    _order = 'id'

    name = fields.Char(string='Paper', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)

class CourseLanguage(models.Model):
    _name = 'course.language'
    _description = 'Course Language'

    name = fields.Char( string='Language', required=True )
    active = fields.Boolean( default=True )

class CoursePlan(models.Model):
    _name = 'course.plan'
    _description = 'Course Plan'

    name = fields.Char( string='Plan', required=True )
    code = fields.Char( string='Code' )
    active = fields.Boolean( default=True )
