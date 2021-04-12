# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    timesheet_account_id = fields.Many2one('account.account', string='Compte des timesheet')