from odoo import api, fields, models, _

class Crm(models.Model):
    _inherit = 'crm.lead'

    course = fields.Char('Course')
    subject = fields.Char('Subject')
    lead_quality = fields.Selection([
        ('hot', 'Hot 🔥'),
        ('warm', 'Warm 🟡'),
        ('cold', 'Cold 🔵'),
    ], string="Lead Quality", tracking=True, required=True)
    student_created = fields.Boolean(string="Student Created", default=False)
    student_id = fields.Many2one("student.student", string="Student")

    def action_open_student(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "student.student",
            "res_id": self.student_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def act_create_student(self):
        print('hi', self.is_won_stage)
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Student',
            'res_model': 'create.student.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_first_name': self.contact_name,
                'default_phone': self.phone,
                'default_email': self.email_from,
            }
        }

class CreateStudentWizard(models.TransientModel):
    _name = "create.student.wizard"
    _description = "Create Student Wizard"

    lead_id = fields.Many2one("crm.lead")

    first_name = fields.Char(required=True)
    last_name = fields.Char("Last Name", required=1)
    phone = fields.Char("Phone", required=1)
    email = fields.Char("Email", required=True)

    course_id = fields.Many2one("product.product", "Course", required=True)
    name = fields.Char(compute="_compute_name", store=True)

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = " ".join(filter(None, [rec.first_name, rec.last_name]))

    def action_create_student(self):
        self.ensure_one()

        student = self.env['student.student'].sudo().create({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name' : self.name,
            'mobile': self.phone,
            'email': self.email,
            'course_id': self.course_id.id,

        })
        self.lead_id.write({
            "student_created": True,
            "student_id": student.id,
        })

