# -*- encoding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import datetime
import os

class sync_analytic_parameter_wizard(models.TransientModel):
    _name = 'sync.analytic.parameter.wizard'

    @api.multi
    def action_validate(self):
        timesheets = self.env['hr_timesheet_sheet.sheet'].search([('id','in',self._context['active_ids'])])
        for timesheet in timesheets:
            timesheet.sync_analytic_parameter()

sync_analytic_parameter_wizard()