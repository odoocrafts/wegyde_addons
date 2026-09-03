from odoo import fields, api,_, models

class AccaPaper(models.Model):
    _name = 'acca.paper'
    _description = 'ACCA Paper'
    name = fields.Char(string='Paper Name', required=True)  # e.g., "FR - Financial Reporting"
    code = fields.Char(string='Code')

class AccaLanguage(models.Model):
    _name = 'acca.language'
    _description = 'Batch Language'
    name = fields.Char(string='Language', required=True)
    # e.g., "English", "Malayalam"
class AccaPlan(models.Model):
    _name = 'acca.plan'
    _description = 'Study Plan'
    name = fields.Char(string='Plan Name', required=True) 