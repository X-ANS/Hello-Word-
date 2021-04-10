# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class analytic_key(models.Model):
    _name = 'analytic.key'
    # _order = 'prorata_type desc, code'
    _order = 'sequence'

    name = fields.Char(string=u'Description',required=True)
    code = fields.Char(string=u'Code',required=True)
    type = fields.Selection(
        [('activity', u'Activité'), ('prestation', 'Prestation')], u'Activité/Prestation',required=True)
    activity_id = fields.Many2one('account.activity', string=u'Activité')
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    auto_compute_tag = fields.Selection([('WEB', 'WEB'), ('MATRICE', 'MATRICE'), ('CLIENT', 'CLIENT')], 'Tag auto calcul')
    prorata_type = fields.Selection(related='prestation_id.prorata_type', store=True)
    sequence = fields.Integer(default=1)


class analytic_key_value(models.Model):
    _name = 'analytic.key.value'
    _rec_name = 'analytic_key_id'

    analytic_key_id = fields.Many2one('analytic.key', string=u'Clé de répartition',required=True)
    type = fields.Selection(related='analytic_key_id.type',string="Type",store=True, readonly=True)
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    value = fields.Float('Valeur', required=True)
    value_date = fields.Date('Date', required=True)
