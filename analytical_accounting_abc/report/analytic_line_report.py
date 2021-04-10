# -*- coding: utf-8 -*-

from openerp import tools
from openerp.osv import fields,osv


class analytic_entries_report(osv.osv):
    _inherit = "analytic.entries.report"

    _columns = {
        'step_id': fields.many2one('analytic.step', 'Etape', readonly=True),
        'prestation_id': fields.many2one('account.prestation', 'Prestation', readonly=True),
        'activity_id': fields.many2one('account.activity', 'Activité', readonly=True),
        'analytical_monthly_id': fields.many2one('account.analytical.monthly', string=u'Arreter analytique'),
        'prestation_source_id': fields.many2one('account.prestation', string=u'Prestation source')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'analytic_entries_report')
        cr.execute("""
            create or replace view analytic_entries_report as (
                 select
                     min(a.id) as id,
                     count(distinct a.id) as nbr,
                     a.date as date,
                     a.user_id as user_id,
                     a.name as name,
                     analytic.partner_id as partner_id,
                     a.company_id as company_id,
                     a.currency_id as currency_id,
                     a.account_id as account_id,
                     a.general_account_id as general_account_id,
                     a.journal_id as journal_id,
                     a.move_id as move_id,
                     a.product_id as product_id,
                     a.product_uom_id as product_uom_id,
                     sum(a.amount) as amount,
                     sum(a.unit_amount) as unit_amount,
                     a.step_id as step_id,
                     a.prestation_id as prestation_id,
                     a.activity_id as activity_id,
                     a.analytical_monthly_id as analytical_monthly_id,
                     a.prestation_source_id as prestation_source_id                     
                     
                 from
                     account_analytic_line a, account_analytic_account analytic
                 where analytic.id = a.account_id
                 group by
                     a.date, a.user_id,a.name,analytic.partner_id,a.company_id,a.currency_id,
                     a.account_id,a.general_account_id,a.journal_id,
                     a.move_id,a.product_id,a.product_uom_id, a.step_id, a.prestation_id,
                     a.activity_id, a.analytical_monthly_id, a.prestation_source_id
            )
        """)
