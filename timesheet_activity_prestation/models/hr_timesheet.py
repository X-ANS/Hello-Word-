# -*- coding: utf-8 -*-

from openerp import api,fields,models
import json
from datetime import timedelta


class AnalyticTimesheet(models.Model):
    _inherit='hr.analytic.timesheet'

    enable_modification = fields.Boolean(string = 'Autoriser Modification Activités')
    activity_id = fields.Many2one('account.activity', string=u'Activité')
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    matricule_employee = fields.Char('Matricule')
    tjm_employee = fields.Float('TJM ',default=1.0)
    emp_id = fields.Many2one('hr.employee', string="Employe" ,required=False)
    sychronised = fields.Boolean(string = 'Sychronisé')
    activity_code = fields.Char('Code Activity')

    @api.onchange('date')
    def on_change_date(self):
        for obj in self:
            date = fields.Date.from_string(obj.date)
            if date.weekday()>=5:
                date = date - timedelta(days=(date.weekday()-4))
                obj.date = date
                self.write({'date': date})

    @api.onchange('activity_id')
    def on_change_activity(self):
        displayed_services = []
        services = self.env['account.prestation'].search([('active', '=', True)])
        for obj in self:
            line_id = obj.line_id
            if line_id:
                line_id.set_activity_prestation(self.activity_id.id,self.prestation_id.id)
        if self.activity_id:
            res = {}
            res['domain'] = {}
            self.activity_code = self.activity_id.code
            if self.activity_id.type == 'direct' and self.activity_id.prestation_ids:
                if len(self.activity_id.prestation_ids) == 1:
                    self.prestation_id = self.activity_id.prestation_ids
                else:
                    self.prestation_id = False
                res['domain']['prestation_id'] = [('id', '=', self.activity_id.prestation_ids.ids)]
            elif self.activity_id.code == 'PROJEC':
                for service in services:
                    if service.processus_id.code =='PRO':
                        displayed_services.append(service.id)
                res['domain']['prestation_id'] = [('id', 'in', displayed_services)]
            else:
                self.prestation_id = False
                res['domain']['prestation_id'] = [('id', 'in', [])]
            return res

    # def onchange_activity_prestation_id(self, cr, uid, ids, activity_id, prestation_id, context=None):
    #     reads = self.read(cr, uid, ids, ['activity_id', 'prestation_id','line_id'], context=context)
    #     res = []
    #     for record in reads:
    #         line_id = record['line_id'][0]
    #         activity_obj = self.pool.get('account.activity').browse(cr, uid, activity_id, context=context)
    #         prestation_obj = self.pool.get('account.prestation').browse(cr, uid, prestation_id, context=context)
    #         if line_id:
    #             analytic_line_id = self.pool.get('account.analytic.line').browse(cr, uid, line_id, context=context)
    #             analytic_line_id.set_activity_prestation(activity_obj.id,prestation_obj.id)
    #         if activity_obj:
    #             res = {}
    #             res['domain'] = {}
    #             if activity_obj.type == 'direct' and activity_obj.prestation_ids:
    #                 if len(activity_obj.prestation_ids) == 1:
    #                     self.write(cr, uid, ids[0], {'prestation_id':activity_obj.prestation_ids[0].id}, context=context)
    #                 else:
    #                     self.write(cr, uid, ids[0], {'prestation_id':False}, context=context)
    #                 res['domain']['prestation_id'] = [('id', '=', activity_obj.prestation_ids.ids)]
    #             else:
    #                 self.write(cr, uid, ids[0], {'prestation_id':False}, context=context)
    #             return res
    #     return True


    @api.onchange('unit_amount')
    def on_change_unitamount(self):
        for obj in self:
            sheet_id = obj.sheet_id
            sheet_id.sync_analytic_parameter()
        return True

    @api.onchange('enable_modification')
    def getDisplayedActivities(self):
        displayed_activities = []
        for record in self:
            if self.emp_id:
                employee_id = self.env['hr.employee'].search([('id', '=', self.emp_id.id)])
            elif self.sheet_id.employee_id:
                employee_id = self.env['hr.employee'].search([('id', '=', self.sheet_id.employee_id.id)])
            activities = self.env['account.activity'].search([('active', '=', True)])
            if employee_id.activity_ids:
                for activity in employee_id.activity_ids:
                    displayed_activities.append(activity.id)
            else:
                for activity in activities:
                    displayed_activities.append(activity.id)
            if employee_id.matricule:
                matricule = employee_id.matricule
                record.matricule_employee = matricule
                record.tjm_employee = employee_id.tjm_employee
            print ""+"[('id', '=',",displayed_activities,")]"
            default_projects = self.env['account.analytic.account'].search([('name', '=', 'ABC')])
            if default_projects:
                record.account_id = default_projects[0].id
        #return  json.dumps([('id', 'in', displayed_activities)])
        return {'domain': {'activity_id': [('id', 'in', displayed_activities)]}}


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'


    def set_activity_prestation(self, cr, uid, ids, activity_id ,prestation_id, context=None):
        return self.write(cr, uid, ids[0], {'activity_id': activity_id,'prestation_id':prestation_id}, context=context)

    def set_amount(self, cr, uid, ids, amount, context=None):
        return self.write(cr, uid, ids[0], {'amount': amount}, context=context)
