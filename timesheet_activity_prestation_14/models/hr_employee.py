# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    activity_ids = fields.Many2many('account.activity', 'activity_employee_rel', 'employee_id',
                                           'activity_id', 'Activités')
    matricule = fields.Char('Matricule')
    tjm_employee = fields.Float('TJM ',default=1.0)
