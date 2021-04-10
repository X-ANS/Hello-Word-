# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class key_activity(models.Model):
    _name = 'key.activity'
    _inherit = ['mail.thread']

    name = fields.Char(string=u'Description',required=True)
    code = fields.Char(string=u'Code',required=True)
    active = fields.Boolean('Actif', default=True)
    key_activity_lines = fields.One2many('key.activity.line','key_activity_id',string=u'Valeurs de la clé')

    @api.one
    @api.constrains('key_activity_lines', 'key_activity_lines.value')
    def _check_sum_values(self):
        if self.key_activity_lines:
            sum_vals = sum([line.value for line in self.key_activity_lines])
            if sum_vals != 100.0:
                raise Warning(_(u"La somme des valeurs des lignes doit être 100!"))


class key_activity_line(models.Model):
    _name = 'key.activity.line'
    activity_id = fields.Many2one('account.activity', string=u'Activité',required=True)
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    key_id = fields.Many2one('analytic.key', string=u'Clé prestation')
    key_activity_id = fields.Many2one('key.activity', string=u'Clé')
    value = fields.Float(string=u'Valeur')





