# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.osv import osv

class AnalyticTimesheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    matricule_employee = fields.Char('Matricule')
    tjm_employee = fields.Char('TJM ')
    compute_modification = fields.Boolean(string='Compute Modification Activités', compute='setEnableModification')

    def button_confirm(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context):
            if sheet.employee_id and sheet.employee_id.parent_id and sheet.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [sheet.id], user_ids=[sheet.employee_id.parent_id.user_id.id], context=context)
            self.check_employee_attendance_state(cr, uid, sheet.id, context=context)
            di = sheet.user_id.company_id.timesheet_max_difference
            for timesheet_id in sheet.timesheet_ids:
                num_hours_day = 0.0
                for timesheet_id_temp in sheet.timesheet_ids:
                    if timesheet_id_temp.date == timesheet_id.date:
                        num_hours_day += timesheet_id_temp.unit_amount
                print 'Num heures 1 == ',abs(num_hours_day-8.0)
                if abs(num_hours_day - 8.0) < 0.0001:
                    print 'Num heures == ',num_hours_day
                else:
                    raise osv.except_osv(_('Warning!'), _('Il faut saisir exactement 8h dans la journée  '+timesheet_id.date))
            if (abs(sheet.total_difference) < di) or not di:
                sheet.signal_workflow('confirm')
            else:
                raise osv.except_osv(_('Warning!'), _('Please verify that the total difference of the sheet is lower than %.2f.') %(di,))
        return True

    def setEnableModification(self):
        for obj in self:
            if obj.state in ('draft', 'new'):
                print "I am goinr to modifie"
                obj.sync_analytic_parameter()
            if obj.timesheet_ids and obj.state in ('draft', 'new'):
                for line in self.timesheet_ids:
                    print "I am goinr to modifie"
                    line.write({'enable_modification': False})

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        department_id =  False
        user_id = False
        if employee_id:
            empl_id = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            department_id = empl_id.department_id.id
            user_id = empl_id.user_id.id
            matricule_employee = empl_id.matricule
            tjm_employee = empl_id.tjm_employee
        return {'value': {'department_id': department_id, 'user_id': user_id,'matricule_employee':matricule_employee,'tjm_employee':tjm_employee}}

    @api.one
    def sync_analytic_parameter(self):
        for obj in self:
            daily_amount = 0
            tjm_form_employee = obj.employee_id.tjm_employee
            tjm_employee = float(tjm_form_employee)
            if obj.timesheet_ids:
                for timesheet_id in obj.timesheet_ids:
                    unit_amount  = timesheet_id.unit_amount
                    if tjm_employee and unit_amount:
                        unit_amount = float(unit_amount/8)
                        daily_amount = tjm_employee*unit_amount
                    timesheet_line_id = timesheet_id.line_id
                    if timesheet_line_id:
                        print " I am Here With Activity ===",timesheet_id.activity_id.id,"And Prestation =====",timesheet_id.prestation_id.id
                        timesheet_line_id.set_activity_prestation(timesheet_id.activity_id.id,timesheet_id.prestation_id.id)
                        timesheet_line_id.set_amount(daily_amount)
                        company_id = self.env['res.company'].browse(1)
                        timesheet_account_id = company_id.timesheet_account_id.id
                        #if timesheet_account_id:
                        #    timesheet_line_id.account_id = timesheet_account_id
                        #else:
                        #    raise ValueError(_("Merci de paramétrer le compte comptable des Timesheet"))
                        timesheet_line_id.sychronised = True
                    else:
                        raise Warning(_('Merci d enregistrer les modifications avant la syshronisation'))







