# -*- coding: utf-8 -*-
from openerp import fields, models, api
from datetime import datetime, time, timedelta
from openerp import exceptions
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    )


class Employee(models.Model):
    _inherit = 'hr.employee'

    activity_ids = fields.Many2many('account.activity', 'activity_employee_rel', 'employee_id',
                                           'activity_id', 'Activités')
    matricule = fields.Char('Matricule')
    tjm_employee = fields.Float('TJM ',default=1.0)
