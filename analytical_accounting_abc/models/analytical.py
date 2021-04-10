# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, netsvc
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class analytic_step(models.Model):
    _name = 'analytic.step'
    _order = 'step'

    name = fields.Char(string=u'Description', required=True)
    code = fields.Char(string=u'Code', required=True)
    step = fields.Integer(string=u"Numéro")
    analytic_key_ids = fields.Many2many(
        'analytic.key', 'step_key_rel',
        string=u'Clés de répartition')
    initial_step = fields.Boolean(u'Etape initiale')

    @api.one
    @api.constrains('initial_step', 'step')
    def _check_unique_initial_step(self):
        if self.initial_step:
            step_ids = self.search([('initial_step', '=', True)])
            if len(step_ids) > 1:
                raise Warning(_(u"Une autre étape est definie comme l'étape initiale!"))
        step_ids = self.search([('step', '=', self.step)])
        if len(step_ids) > 1:
            raise Warning(_(u"Le numéro de l'étape doit être unique!"))


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    analytical_monthly_id = fields.Many2one('account.analytical.monthly', string=u'Arreter analytique')
    step_id = fields.Many2one('analytic.step', string=u'Etape de réallocation')
    prestation_source_id = fields.Many2one('account.prestation', string=u'Prestation source')


class account_analytical_monthly_line(models.Model):
    _name = "account.analytical.monthly.line"

    step_id = fields.Many2one('analytic.step', string=u'Etape')
    analytical_monthly_id = fields.Many2one('account.analytical.monthly', string=u'Arreter analytique')

    @api.multi
    def action_activity_lines(self):
        for record in self:
            return {'name': _('Lignes analytiques'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.analytic.line',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'domain': [('step_id', '=', record.step_id.id),
                               ('analytical_monthly_id', '=', record.analytical_monthly_id.id)],
                    'context': {'group_by': ['activity_id']},
                    }

    @api.multi
    def action_prestation_lines(self):
        for record in self:
            return {'name': _('Lignes analytiques'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.analytic.line',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'domain': [('step_id', '=', record.step_id.id),
                               ('analytical_monthly_id', '=', record.analytical_monthly_id.id)],
                    'context': {'group_by': ['prestation_id']},
                    }


class account_analytical_monthly(models.Model):
    _name = "account.analytical.monthly"
    _inherit = ['mail.thread']
    _description = "Arreter analytique"
    _order = "date_debut desc, date_fin desc"

    @api.multi
    def unlink(self):
        for rec in self:
            rec.analytical_account_ids.unlink()
            rec.step_ids.unlink()
        res = super(account_analytical_monthly, self).unlink()
        return res

    @api.multi
    def step_zero(self):
        print("step_zero")
        analytic_obj = self.env['account.analytic.line']
        presta_obj = self.env['account.prestation']
        step_id = self.env['analytic.step'].search([('initial_step', '=', True)])
        if not step_id:
            raise Warning(_(u"Aucune étape initiale n'est définie pour les étapes de réallocation!"))
        for record in self:
            self.env.cr.execute(
                """SELECT ID FROM account_analytic_line WHERE  date>=%s AND date<=%s AND step_id is NULL;""",
                (self.date_debut, self.date_fin))
            sql_lines = self.env.cr.fetchall()
            line_ids = analytic_obj.search([('date', '<=', self.date_fin),
                                            ('date', '>=', self.date_debut), ('step_id', '=', False)])
            self.env.cr.execute(
                """SELECT prestation_id,sum(amount) FROM account_analytic_line WHERE  date>=%s AND date<=%s AND
                 prestation_id is NOT NULL and step_id is NULL GROUP BY prestation_id;""",
                (self.date_debut, self.date_fin))
            sql_presta = self.env.cr.dictfetchall()
            self.env.cr.execute(
                """SELECT sum(amount) FROM account_analytic_line WHERE  date>=%s AND date<=%s AND prestation_id is NOT NULL and step_id is NULL;""",
                (self.date_debut, self.date_fin))
            total_amount = self.env.cr.fetchone()[0]


            presta_dict = {}
            for line in sql_presta:
                presta_dict[line['prestation_id']] = line['sum']

            self.env.cr.execute(
                """SELECT prestation_id, sum(unit_amount) FROM account_analytic_line WHERE  
                date>=%s AND date<=%s AND prestation_id is NOT NULL and general_account_id = %s and step_id is NULL
                GROUP BY prestation_id;""",
                (self.date_debut, self.date_fin, self.timesheet_account_id.id))
            sql_upd_manday = self.env.cr.dictfetchall()

            self.env.cr.execute(
                """SELECT sum(unit_amount) FROM account_analytic_line WHERE  date>=%s AND date<=%s AND 
                prestation_id is NOT NULL and general_account_id = %s and step_id is NULL;""",
                (self.date_debut, self.date_fin, self.timesheet_account_id.id))
            presta_total_manday = self.env.cr.fetchone()[0]

            presta_manday_dict = {}
            for line in sql_upd_manday:
                presta_manday_dict[line['prestation_id']] = line['sum']

            # Traitement du type direct
            self.env.cr.execute(
                """SELECT al.ID , al.account_id, al.amount, al.unit_amount, al.date, al.name, al.general_account_id, 
                al.product_uom_id, al.journal_id, al.product_id, al.activity_id, al.prestation_id
                FROM account_analytic_line al, account_activity act 
                    WHERE  al.step_id is NULL and act.id=al.activity_id
                    and act.type = 'direct' and  al.date>=%s AND 
                    al.date<=%s AND step_id is NULL;""",
                (self.date_debut, self.date_fin))

            sql_direct_line = self.env.cr.dictfetchall()
            for line_sql in sql_direct_line:

                # self.env.cr.execute("""
                # select account_id, amount, unit_amount, date, name, general_account_id, product_uom_id, journal_id,
                #  product_id, activity_id, prestation_id from account_analytic_line
                # where id =%s
                # """, ((l_direct['id'],)))
                # line_sql = self.env.cr.dictfetchone()
                if line_sql['prestation_id'] == None:
                    activite = self.env['account.activity'].browse(line_sql['activity_id'])
                    raise ValidationError("Une ligne avec l'activité directe %s est sans prestation"%(str(activite.code)))
                self.env.cr.execute("""
                insert into account_analytic_line 
                (account_id, amount, unit_amount, date, name, general_account_id,
                 product_uom_id, journal_id, product_id, activity_id, prestation_id, 
                 analytical_monthly_id,step_id)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (line_sql['account_id'],
                      line_sql['amount'],
                      line_sql['unit_amount'],
                      line_sql['date'],
                      line_sql['name'],
                      line_sql['general_account_id'],
                      line_sql['product_uom_id'],
                      line_sql['journal_id'],
                      line_sql['product_id'],
                      line_sql['activity_id'],
                      line_sql['prestation_id'],
                      record.id,
                      step_id.id
                      ))

            # Traitement du type indirect
            indirect_lines = line_ids.filtered(lambda l: l.activity_id.type == 'indirect')
            for l_indirect in indirect_lines:
                key_ids = self.env['analytic.key'].search(
                    [('activity_id', '=', l_indirect.activity_id.id), ('type', '=', 'activity')])
                if len(key_ids) != 1:
                    raise Warning(_(u"Une et une seule clé doit être définie pour l'activité indirecte %s!" % (
                        l_indirect.activity_id.name)))
                key = key_ids[0]
                key_val_ids = self.env['analytic.key.value'].read_group([('analytic_key_id', '=', key.id)]
                                                                        , ['prestation_id', 'value'], ['prestation_id'])
                key_val_dict = {}
                for val in key_val_ids:
                    key_val_dict[val['prestation_id'][0]] = val['value']
                sum_ratio = sum(key_val_dict.values())
                for presta in key_val_dict:
                    ratio = key_val_dict[presta] / (sum_ratio or 1.0)
                    unit_amount = l_indirect.unit_amount
                    if l_indirect.general_account_id.id == self.timesheet_account_id.id:
                        unit_amount = ratio * l_indirect.unit_amount
                    # self.env.cr.execute("""
                    #                 select account_id, date, name, general_account_id, product_uom_id, journal_id, product_id, activity_id
                    #                 from account_analytic_line
                    #                 where id =%s
                    #                 """, ((l_indirect.id,)))
                    # line_sql = self.env.cr.dictfetchone()

                    self.env.cr.execute("""
                                    insert into account_analytic_line (account_id,amount, unit_amount, date, name, general_account_id, product_uom_id, journal_id, product_id, activity_id,prestation_id, analytical_monthly_id,step_id)
                                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                    """, (l_indirect.account_id.id or None,
                                          l_indirect.amount * ratio,
                                          unit_amount,
                                          l_indirect.date,
                                          l_indirect.name,
                                          l_indirect.general_account_id.id or None,
                                          l_indirect.product_uom_id.id or None,
                                          l_indirect.journal_id.id or None,
                                          l_indirect.product_id.id or None,
                                          l_indirect.activity_id.id or None,
                                          presta,
                                          record.id,
                                          step_id.id
                                          ))
                    if presta_dict.get(presta, False):
                        presta_dict[presta] += l_indirect.amount * ratio
                    else:
                        presta_dict[presta] = l_indirect.amount * ratio
                    if l_indirect.general_account_id.id == self.timesheet_account_id.id:
                        if presta_manday_dict.get(presta, False):
                            presta_manday_dict[presta] += unit_amount
                            presta_total_manday += unit_amount
                        else:
                            presta_manday_dict[presta] = unit_amount
                            presta_total_manday += unit_amount

            # Traitement du type prorata
            if total_amount != 0:

                prorata_lines = line_ids.filtered(lambda l: l.activity_id.type == 'prorata').sorted(
                    key=lambda r: r.activity_id.len_process)
                for l_prorata in prorata_lines:

                    presta_ids = presta_obj.search([('id', 'in', presta_dict.keys()), (
                    'processus_id', 'in', [pr_id.id for pr_id in l_prorata.activity_id.processus_ids])])
                    sum_ratio = 0.0
                    for presta in presta_ids:
                        sum_ratio += presta_dict[presta.id]
                    for presta in presta_ids:
                        if presta_dict[presta.id] != 0:
                            ratio = presta_dict[presta.id] / (sum_ratio or 1.0)
                            unit_amount = l_prorata.unit_amount
                            if l_prorata.general_account_id.id == self.timesheet_account_id.id:
                                unit_amount = ratio * l_prorata.unit_amount
                            # self.env.cr.execute("""select account_id,date, name, general_account_id, product_uom_id,
                            #  journal_id, product_id, activity_id from account_analytic_line
                            #                                     where id =%s
                            #                                     """, ((l_prorata.id,)))
                            # line_sql = self.env.cr.dictfetchone()

                            self.env.cr.execute("""
                                    insert into account_analytic_line (account_id,amount, unit_amount, date, name, 
                                    general_account_id, product_uom_id, journal_id, product_id, activity_id,
                                    prestation_id, analytical_monthly_id,step_id)
                                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                    """, (l_prorata.account_id.id or None,
                                          l_prorata.amount * ratio,
                                          unit_amount,
                                          l_prorata.date,
                                          l_prorata.name,
                                          l_prorata.general_account_id.id or None,
                                          l_prorata.product_uom_id.id or None,
                                          l_prorata.journal_id.id or None,
                                          l_prorata.product_id.id or None,
                                          l_prorata.activity_id.id or None,
                                          presta.id,
                                          record.id,
                                          step_id.id
                                          ))
                            if presta_dict.get(presta.id, False):
                                presta_dict[presta.id] += l_prorata.amount * ratio
                            else:
                                presta_dict[presta.id] = l_prorata.amount * ratio

                            if presta_manday_dict.get(presta.id, False) and\
                                    l_prorata.general_account_id.id == self.timesheet_account_id.id:
                                presta_manday_dict[presta.id] += unit_amount
                                presta_total_manday += unit_amount
                            elif not presta_manday_dict.get(presta.id, False) and \
                                    l_prorata.general_account_id.id == self.timesheet_account_id.id:
                                presta_manday_dict[presta.id] = unit_amount
                                presta_total_manday += unit_amount


            # Traitement du type manday
            manday_lines = line_ids.filtered(lambda l: l.activity_id.type == 'manday')
            for l_manday in manday_lines:
                presta_ids = presta_obj.search([('id', 'in', presta_dict.keys()), (
                    'processus_id', 'in', [pr_id.id for pr_id in l_manday.activity_id.processus_ids])])
                for presta in presta_ids:
                    if presta_manday_dict.get(presta.id, False) and presta_manday_dict[presta.id] != 0:
                        unit_amount = l_manday.unit_amount
                        if l_manday.general_account_id.id == self.timesheet_account_id.id:
                            unit_amount = l_manday.unit_amount * presta_manday_dict[presta.id] / (
                                        presta_total_manday or 1.0)
                        # self.env.cr.execute("""select account_id,date, name, general_account_id, product_uom_id,
                        # journal_id, product_id, activity_id from account_analytic_line
                        # where id =%s
                        #     """, ((l_manday.id,)))
                        # line_sql = self.env.cr.dictfetchone()

                        self.env.cr.execute("""
                        insert into account_analytic_line (account_id,amount, unit_amount, date, name, general_account_id, product_uom_id, journal_id, product_id, activity_id,prestation_id, analytical_monthly_id,step_id)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (l_manday.account_id.id or None,
                              presta_manday_dict[presta.id] * l_manday.amount / (presta_total_manday or 1.0),
                              unit_amount,
                              l_manday.date,
                              l_manday.name,
                              l_manday.general_account_id.id or None,
                              l_manday.product_uom_id.id or None,
                              l_manday.journal_id.id or None,
                              l_manday.product_id.id or None,
                              l_manday.activity_id.id or None,
                              presta.id,
                              record.id,
                              step_id.id
                              ))

            self.env['account.analytical.monthly.line'].create({
                'step_id': step_id.id,
                'analytical_monthly_id': record.id,
            })

    @api.multi
    def clean_unit(self):
        analytic_obj = self.env['account.analytic.line']
        line_ids = analytic_obj.search([('date', '<=', self.date_fin),
                                        ('date', '>=', self.date_debut), ('step_id', '=', False)])
        for line in line_ids:
            if line.general_account_id.id != self.timesheet_account_id.id:
                line.unit_amount = 0

    def get_cost_entries(self, presta_ids, analytical_monthly_id, step_id):
        self.env.cr.execute("""SELECT prestation_id,sum(amount) as amount
                                        from account_analytic_line
                                        where amount<0 and analytical_monthly_id =%s  and step_id = %s and prestation_id in %s
                                        group by prestation_id""",
                            (analytical_monthly_id, step_id, tuple(presta_ids)))
        return self.env.cr.dictfetchall()

    def get_margin_entries(self, presta_ids, analytical_monthly_id, step_id):
        self.env.cr.execute("""SELECT prestation_id,sum(amount) as amount
                                        from account_analytic_line
                                        where analytical_monthly_id =%s  and step_id = %s and prestation_id in %s
                                        group by prestation_id
                                        having sum(amount) > 0""",
                            (analytical_monthly_id, step_id, tuple(presta_ids)))
        return self.env.cr.dictfetchall()

    @api.multi
    def execute_steps_prestation(self, step, line_ids, record,presta_process_dict):
        print 'execute_steps_prestation', len(line_ids)
        key_dict = {}
        for key in step.key_ids:
            if key.type == 'prestation' and key.prestation_id:
                key_val_dict = {}
                if not key.prestation_id.prorata_type:
                    key_val_ids = self.env['analytic.key.value'].read_group([('analytic_key_id', '=', key.id)]
                                                                            , ['prestation_id', 'value'],
                                                                            ['prestation_id'])
                    for val in key_val_ids:
                        key_val_dict[val['prestation_id'][0]] = val['value']
                    key_dict[key.prestation_id.id] = key_val_dict
        for line in line_ids:
            if line['prestation_id'] in key_dict.keys():
                for elems in key_dict[line['prestation_id']]:
                    elem_vals = key_dict[line['prestation_id']][elems]
                    elems_total = sum(key_dict[line['prestation_id']].values())
                    if elems_total != 0:
                        unit_amount = line['unit_amount']
                        if line['general_account_id'] == self.timesheet_account_id.id:
                            unit_amount = line['unit_amount'] * elem_vals / elems_total
                        self.env.cr.execute("""
                                            insert into account_analytic_line (account_id,amount, unit_amount, date, name, general_account_id, product_uom_id, journal_id,
                                            activity_id,prestation_id, analytical_monthly_id,step_id,prestation_source_id,product_id,prestation_pro_id)
                                            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                            """, (line['account_id'],
                                                  elem_vals * line['amount'] / elems_total,
                                                  unit_amount,
                                                  line['date'],
                                                  '/',
                                                  line['general_account_id'],
                                                  line['product_uom_id'],
                                                  line['journal_id'],
                                                  # line_sql['product_id'],
                                                  line['activity_id'],
                                                  elems,
                                                  record.id,
                                                  step.step_id.id,
                                                  line['prestation_id'],
                                                  line['product_id'],
                                                  presta_process_dict[elems]
                                                  ))

    @api.multi
    def execute_steps_no_key_prestation(self, step, line_ids, record, presta_process_dict):
        print 'execute_steps_no_key_prestation', len(line_ids)
        key_dict = {}
        for key in step.key_ids:
            if key.type == 'prestation' and key.prestation_id:
                key_val_dict = {}
                if key.prestation_id.prorata_type:
                    key_val_ids = []
                    presa_ids = []
                    if key.prestation_id.prorata_processus_id:
                        presa_ids = self.env['account.prestation'].search(
                            [('processus_id', '=', key.prestation_id.prorata_processus_id.id)]).mapped('id')
                    if key.prestation_id.prestation_ids:
                        presa_ids = [p.id for p in key.prestation_id.prestation_ids]
                    if presa_ids:
                        if key.prestation_id.prorata_type == 'cost':
                            key_val_ids = self.get_cost_entries(presa_ids, record.id, step.id)
                        if key.prestation_id.prorata_type == 'margin':
                            key_val_ids = self.get_margin_entries(presa_ids, record.id, step.id)
                        for val in key_val_ids:
                            key_val_dict[val['prestation_id']] = val['amount']
                        key_dict[key.prestation_id.id] = key_val_dict
                if not key.prestation_id.prorata_type:
                    key_val_ids = self.env['analytic.key.value'].read_group([('analytic_key_id', '=', key.id)]
                                                                            , ['prestation_id', 'value'],
                                                                            ['prestation_id'])
                    for val in key_val_ids:
                        key_val_dict[val['prestation_id'][0]] = val['value']
                    key_dict[key.prestation_id.id] = key_val_dict
        for line in line_ids:
            if not line['prestation_id'] in key_dict.keys():
                self.env.cr.execute("""
                                                        insert into account_analytic_line (account_id, amount, unit_amount, date, name, general_account_id, product_uom_id,
                                                        journal_id, activity_id, prestation_id, analytical_monthly_id,step_id,product_id,prestation_source_id,prestation_pro_id)
                                                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                                        """, (line['account_id'],
                                                              line['amount'],
                                                              line['unit_amount'],
                                                              line['date'],
                                                              '/',
                                                              line['general_account_id'],
                                                              line['product_uom_id'],
                                                              line['journal_id'],
                                                              # line_sql['product_id'],
                                                              line['activity_id'],
                                                              line['prestation_id'],
                                                              record.id,
                                                              step.step_id.id,
                                                              line['product_id'],
                                                              line['prestation_id'],
                                                              presta_process_dict[line['prestation_id']]
                                                              ))

    @api.multi
    def execute_steps_prestation_prorata(self, step, line_ids, record, presta_process_dict):
        print 'execute_steps_prestation_prorata', len(line_ids)
        key_dict = {}
        for key in step.key_ids:
            if key.type == 'prestation' and key.prestation_id:
                key_val_dict = {}
                if key.prestation_id.prorata_type:
                    key_val_ids = []
                    presa_ids = []
                    if key.prestation_id.prorata_processus_id:
                        presa_ids = self.env['account.prestation'].search(
                            [('processus_id', '=', key.prestation_id.prorata_processus_id.id)]).mapped('id')
                    if key.prestation_id.prestation_ids:
                        presa_ids = [p.id for p in key.prestation_id.prestation_ids]
                    if presa_ids:
                        if key.prestation_id.prorata_type == 'cost':
                            key_val_ids = self.get_cost_entries(presa_ids, record.id, step.step_id.id)
                        if key.prestation_id.prorata_type == 'margin':
                            key_val_ids = self.get_margin_entries(presa_ids, record.id, step.step_id.id)
                        for val in key_val_ids:
                            key_val_dict[val['prestation_id']] = val['amount']
                        key_dict[key.prestation_id.id] = key_val_dict
        for line in line_ids:
            if line['prestation_id'] in key_dict.keys():
                for elems in key_dict[line['prestation_id']]:
                    print('fffff', elems)
                    elem_vals = key_dict[line['prestation_id']][elems]
                    elems_total = sum(key_dict[line['prestation_id']].values())
                    if elems_total != 0:
                        unit_amount = line['unit_amount']
                        if line['general_account_id'] == self.timesheet_account_id.id:
                            unit_amount = line['unit_amount'] * elem_vals / elems_total
                        self.env.cr.execute("""
                                                insert into account_analytic_line (account_id,amount, unit_amount, date,
                                                 name, general_account_id, product_uom_id, journal_id,
                                                activity_id, prestation_id, analytical_monthly_id,step_id,
                                                prestation_source_id,product_id, prestation_pro_id)
                                                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                                """, (line['account_id'],
                                                      elem_vals * line['amount'] / elems_total,
                                                      unit_amount,
                                                      line['date'],
                                                      '/',
                                                      line['general_account_id'],
                                                      line['product_uom_id'],
                                                      line['journal_id'],
                                                      # line_sql['product_id'],
                                                      line['activity_id'],
                                                      elems,
                                                      record.id,
                                                      step.step_id.id,
                                                      line['prestation_id'],
                                                      line['product_id'],
                                                      presta_process_dict[elems]
                                                      ))

    @api.multi
    def execute_steps(self):
        for record in self:
            step_id = self.env['analytic.step'].search([('initial_step', '=', True)])
            step_ids = record.step_to_use_ids.filtered(lambda r: r.step_id.initial_step == False).sorted(
                key=lambda r: r.sequence)
            self.env.cr.execute("""SELECT id, processus_id from account_prestation """,
                                (record.id, step_id.id))
            process_dict = self.env.cr.dictfetchall()
            presta_process_dict = {item['id']:item['processus_id'] for item in process_dict}
            for step in step_ids:
                print('prev step %s' % (step_id.step))
                print("step %s" % (step.step_id.name))
                self.env.cr.execute("""SELECT prestation_id, sum(unit_amount) as unit_amount, product_uom_id, min(date) as date,
                                 sum(amount) as amount, account_id, activity_id, min(general_account_id) as general_account_id ,
                                 min(journal_id) as journal_id, product_id as product_id
                                from account_analytic_line
                                 where analytical_monthly_id =%s  and step_id = %s
                                group by activity_id, prestation_id, product_uom_id, account_id, product_id """,
                                    (record.id, step_id.id))
                line_ids = self.env.cr.dictfetchall()
                self.execute_steps_prestation(step, line_ids, record, presta_process_dict)
                self.execute_steps_no_key_prestation(step, line_ids, record, presta_process_dict)
                self.execute_steps_prestation_prorata(step, line_ids, record, presta_process_dict)
                step_id = step.step_id
                self.env['account.analytical.monthly.line'].create({
                    'step_id': step.step_id.id,
                    'analytical_monthly_id': record.id,
                })
    @api.multi
    def generate_key_values_action(self):
        self.generate_gu_values()
        self.generate_key_values()
        self.write({"state": "key_generated"})

    @api.multi
    def generate_gu_values(self):
        for rec in self:
            print('self.date_debut', rec.date_debut)

            old_web_lines = self.env.cr.execute("""Delete from portnet_web where date >= '%s' and date <= '%s'"""%(rec.date_debut,
                                                                                                           rec.date_fin))
            old_ops_lines = self.env.cr.execute("""Delete from portnet_doc_ops where date >=  '%s'  and date <=  '%s' """%(rec.date_debut,
                                                                                                           rec.date_fin))
            old_client_lines = self.env.cr.execute("""Delete from portnet_client where date >=  '%s'  and date <=  '%s' """%(rec.date_debut,
                                                                                                           rec.date_fin))
            self.env.cr.commit()


            self.env.cr.execute("""Select code_externe, id from account_prestation""")
            prestation_data = self.env.cr.dictfetchall()
            presta_dict = {p['code_externe']: p['id'] for p in prestation_data}

            self.env.cr.execute("""Select code_externe, id from portnet_ops""")
            ops_data = self.env.cr.dictfetchall()
            ops_dict = {p['code_externe']: p['id'] for p in ops_data}
            #################### WEB
            self.env.cr.execute("""Select code_odoo, date_op, sum(nombre_operation) as num_op , type_document 
            from donnees_agregees_odoo where date_op >=  '%s'  and date_op <=  '%s'  
                                            group by code_odoo,type_document,  date_op"""
                                           %(rec.date_debut, rec.date_fin))
            web_data = self.env.cr.dictfetchall()

            for line in web_data:
                if line['code_odoo'] not in presta_dict:
                    raise ValidationError("Le Document  avec le code extrene %s n'est pas disponible"
                                          %(line['code_odoo']))
                else:
                    self.env.cr.execute("""Insert into portnet_web (name, num, date) values (%s, %s, '%s') """
                                        %(presta_dict[line['code_odoo']], line['num_op'] , line['date_op']))
            self.env.cr.commit()
            #################### PORTNET OPS

            self.env.cr.execute("""Select type_document, code_odoo, code_operation, operation, date_op, nombre_operation as num_op 
                                    from donnees_agregees_odoo where date_op >=  '%s'  and date_op <=  '%s'  
                                   """
                                % (rec.date_debut, rec.date_fin))
            doc_ops_data = self.env.cr.dictfetchall()
            for line in doc_ops_data:
                if line['code_odoo'] not in presta_dict:

                    raise ValidationError("Le Document  avec le code extrene %s n'est pas disponible" % (
                    line['code_odoo']))
                elif line['code_operation'] not in ops_dict:
                    raise ValidationError("L'opération avec le code extrene %s n'est pas disponible" % (
                     str(line['code_operation'])))
                else:
                    self.env.cr.execute("""Insert into portnet_doc_ops (name, num, date, op_id) values (%s, %s, '%s', %s) """
                                        % (presta_dict[line['code_odoo']], line['num_op'], line['date_op'],
                                           ops_dict[line['code_operation']]))
            self.env.cr.commit()

            #################### PORTNET client

            self.env.cr.execute("""Select code_odoo, operateur, code_operateur, client, nombre_operation as num_op , date_operation
                                    from donnees_detaillees_odoo where date_operation >=  '%s'  and date_operation <=  '%s'  
                                   """
                                % (rec.date_debut, rec.date_fin))
            client_data = self.env.cr.dictfetchall()
            for line in client_data:
                if line['code_odoo'] not in presta_dict:
                    raise ValidationError("La catégorie client  avec le code extrene %s n'est pas disponible" % (
                    line['code_odoo']))
                elif line['code_operateur'] not in presta_dict:
                    raise ValidationError("L'operateur avec le code extrene %s n'est pas disponible" % (
                     str(line['code_operateur'])))
                else:
                    self.env.cr.execute("""Insert into portnet_client (name, num, date, client_categ_id) values (%s, %s, '%s', %s) """
                                        % ( presta_dict[line['code_operateur']], line['num_op'], line['date_operation'],
                                           presta_dict[line['code_odoo']]))
            self.env.cr.commit()

    @api.multi
    def generate_key_values(self):
        akv_obj = self.env['analytic.key.value']
        doc_ops_obj = self.env['portnet.doc.ops']
        matrix_obj = self.env['portnet.matrix']
        for rec in self:
            step_ids = rec.step_to_use_ids.filtered(lambda r: r.step_id.initial_step == False).sorted(
                key=lambda r: r.sequence)
            for step in step_ids:
                for key in step.key_ids.filtered("auto_compute_tag"):
                    if key.auto_compute_tag == 'EDI':
                        edi_values = self.env['portnet.edi'].search([('date', '<=', rec.date_fin),
                                                                     ('date', '>=', rec.date_debut)])
                        old_values = akv_obj.search([('analytic_key_id', '=', key.id)])
                        old_values.unlink()
                        for val in edi_values:
                            akv_obj.create({
                                'analytic_key_id': key.id,
                                'type': 'prestation',
                                'prestation_id': val.name.id,
                                'value': val.num,
                                'value_date': val.date,
                            })
                    if key.auto_compute_tag == 'FS':
                        fs_values = self.env['portnet.fs'].search([('date', '<=', rec.date_fin),
                                                                   ('date', '>=', rec.date_debut)])
                        old_values = akv_obj.search([('analytic_key_id', '=', key.id)])
                        old_values.unlink()
                        for val in fs_values:
                            akv_obj.create({
                                'analytic_key_id': key.id,
                                'type': 'prestation',
                                'prestation_id': val.name.id,
                                'value': val.num,
                                'value_date': val.date,
                            })
                    if key.auto_compute_tag == 'WEB':
                        web_values = self.env['portnet.web'].search([('date', '<=', rec.date_fin),
                                                                     ('date', '>=', rec.date_debut)])
                        old_values = akv_obj.search([('analytic_key_id', '=', key.id)])
                        old_values.unlink()
                        for val in web_values:
                            akv_obj.create({
                                'analytic_key_id': key.id,
                                'type': 'prestation',
                                'prestation_id': val.name.id,
                                'value': val.num,
                                'value_date': val.date,
                            })
                    if key.auto_compute_tag == 'MATRICE':
                        old_values = akv_obj.search([('analytic_key_id', '=', key.id)])
                        old_values.unlink()
                        doc_ops = doc_ops_obj.search([('name', '=', key.prestation_id.id)])
                        for el in doc_ops:
                            el_matrix = matrix_obj.search([('op_id', '=', el.op_id.id)])
                            if el_matrix:
                                for categ in el_matrix.client_categ_ids:
                                    akv_obj.create({
                                        'analytic_key_id': key.id,
                                        'type': 'prestation',
                                        'prestation_id': categ.id,
                                        'value': el.num / (len(el_matrix.client_categ_ids) or 1.0),
                                        'value_date': el.date,
                                    })
                    if key.auto_compute_tag == 'CLIENT':
                        web_values = self.env['portnet.client'].search([('date', '<=', rec.date_fin),
                                                                        ('date', '>=', rec.date_debut),
                                                                        ('client_categ_id', '=', key.prestation_id.id)])
                        old_values = akv_obj.search([('analytic_key_id', '=', key.id)])
                        old_values.unlink()
                        for val in web_values:
                            akv_obj.create({
                                'analytic_key_id': key.id,
                                'type': 'prestation',
                                'prestation_id': val.name.id,
                                'value': val.num,
                                'value_date': val.date,
                            })

    @api.multi
    def generate_values(self):
        if self.date_fin < self.date_debut:
            raise ValidationError('La date début doit être antérieure a la date fin')
        self.clean_unit()
        # self.generate_key_values()
        self.step_zero()
        self.execute_steps()
        self.write({'state': 'inprogress'})
        return True

    @api.multi
    def to_draft(self):
        self.env.cr.execute("""
                delete from account_analytic_line 
                where analytical_monthly_id =%s
                """, ((self.id,)))
        self.step_ids.unlink()
        self.write({'state': 'draft'})
        return True

    @api.multi
    def validate_entries(self):
        self.write({'state': 'done'})
        return True

    @api.multi
    def compute_timesheet_account(self):
        for rec in self:
            if rec.create_uid.company_id.timesheet_account_id:
                rec.timesheet_account_id = rec.create_uid.company_id.timesheet_account_id.id

    name = fields.Char(string='Description', required=True)
    date_debut = fields.Date(string='Date début', required=True)
    date_fin = fields.Date(string='Date fin', required=True)
    timesheet_account_id = fields.Many2one('account.account', string='Compte des feuilles de temps',
                                           compute='compute_timesheet_account')
    state = fields.Selection([
        ('draft', 'Nouveau'),
        ('key_generated', 'Valeurs de Clés générées'),
        ('inprogress', 'Encours'),
        ('done', u'Côlturé'),
    ], string='Etat', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    analytical_account_ids = fields.One2many('account.analytic.line', 'analytical_monthly_id',
                                             string='Lignes analytiques', readonly=True)
    step_ids = fields.One2many('account.analytical.monthly.line', 'analytical_monthly_id', string=u'Valeurs des étapes',
                               readonly=True)
    step_to_use_ids = fields.One2many('account.analytical.steps.line', 'analytical_monthly_id',
                                      string='Etape de réallocation')


class account_analytical_steps_line(models.Model):
    _name = 'account.analytical.steps.line'
    _order = 'sequence, id'

    sequence = fields.Integer('Séquence', default=1)
    step_id = fields.Many2one('analytic.step', 'Etape')
    analytical_monthly_id = fields.Many2one('account.analytical.monthly')
    key_ids = fields.Many2many('analytic.key', string=u'Clés de répartition')

    @api.onchange('step_id')
    def onchange_step(self):
        self.ensure_one()
        if self.step_id:
            self.sequence = self.step_id.step
            self.key_ids = [(4, l.id) for l in self.step_id.analytic_key_ids]
