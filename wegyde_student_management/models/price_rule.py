from odoo import api, fields, models, tools

class AccaFeeMatrix(models.Model):
    """Admin pre-sets prices for all combinations here"""
    _name = 'acca.fee.matrix'
    _description = 'ACCA Master Fee Matrix'
    _rec_name = 'display_name'
    paper_id = fields.Many2one('acca.paper', string='Paper', required=True)
    language_id = fields.Many2one('acca.language', string='Language', required=True)
    plan_id = fields.Many2one('acca.plan', string='Plan', required=True)
    price = fields.Float(string='Price', required=True)
    display_name = fields.Char(string='Combination', compute='_compute_display_name', store=True)
    _sql_constraints = [
        ('unique_combination', 'unique(paper_id, language_id, plan_id)',
         'A price for this exact Paper, Language, and Plan already exists!')
    ]
    @api.depends('paper_id', 'language_id', 'plan_id', 'price')
    def _compute_display_name(self):
        for rec in self:
            p_name = rec.paper_id.name or ''
            l_name = rec.language_id.name or ''
            pl_name = rec.plan_id.name or ''
            rec.display_name = f"{p_name} | {l_name} | {pl_name} -> {rec.price}"
