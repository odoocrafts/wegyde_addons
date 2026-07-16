from odoo import api, fields, models, _

class Crm(models.Model):
    _inherit = 'crm.lead'

    course = fields.Char('Course')
    subject = fields.Char('Subject')
