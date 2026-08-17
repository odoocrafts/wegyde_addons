# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    razorpay_key_id = fields.Char("Razorpay Key ID", config_parameter='acca_registration.razorpay_key_id')
    razorpay_key_secret = fields.Char("Razorpay Key Secret", config_parameter='acca_registration.razorpay_key_secret')
    razorpay_webhook_secret = fields.Char("Razorpay Webhook Secret", config_parameter='acca_registration.razorpay_webhook_secret')
    acca_default_fee = fields.Float("Default Registration Fee", config_parameter='acca_registration.default_fee', default=0.0)
