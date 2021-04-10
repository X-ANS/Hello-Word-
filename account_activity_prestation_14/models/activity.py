# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class account_activity(models.Model):
    _name = 'account.activity'
    _inherit = ['mail.thread']
    _rec_name='code'
    _order = 'len_process'

    def name_get(self):

        return [(act.id, act.name) for act in self]

    name = fields.Char(string=u'Description',required=True)
    code = fields.Char(string=u'Code',required=True)
    active = fields.Boolean('Actif', default=True)
    processus_ids = fields.Many2many(
        'account.processus', 'activity_processus_rel',
        string='Processus', required=True)
    type = fields.Selection([('direct', 'Direct'),('indirect', 'Indirect'), ('prorata', 'Prorata'),('manday', 'Manday')], 'Type',required=True)
    description = fields.Text(u'Description Inducteur Activité')
    prestation_ids = fields.Many2many('account.prestation', 'activity_prestation_rel',
        string=u'Prestations liées')
    activity_attribute_a_id = fields.Many2one('activity.attribute.a', string=u"Attribut d'Activité A")
    activity_attribute_b_id = fields.Many2one('activity.attribute.b', string=u"Attribut d'Activité B")
    activity_attribute_c_id = fields.Many2one('activity.attribute.c', string=u"Attribut d'Activité C")
    activity_attribute_d_id = fields.Many2one('activity.attribute.d', string=u"Attribut d'Activité D")
    activity_attribute_e_id = fields.Many2one('activity.attribute.e', string=u"Attribut d'Activité E")
    len_process = fields.Integer(compute='compute_len_process', store=True)

    @api.depends('processus_ids')
    def compute_len_process(self):
        for rec in self:
            rec.len_process = len(rec.processus_ids)
