# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, except_orm, ValidationError, RedirectWarning


class account_macro_prestation(models.Model):
    _name = 'account.macro.prestation'

    name = fields.Char(string=u'Description')


class account_prestation_phase(models.Model):
    _name = 'account.prestation.phase'

    name = fields.Char(string=u'Description')

class account_prestation(models.Model):
    _name = 'account.prestation'
    _rec_name = 'code'
    _inherit = ['mail.thread']

    def name_get(self):
        return [(prest.id, prest.name) for prest in self]

    @api.model
    def create(self, vals):
        if not vals.get('processus_id', False):
            raise ValueError('Merci de saisir le processus')
        if not vals.get('code_externe', False) or vals['code_externe'] == '/':
            processus = self.env['account.processus'].browse(vals['processus_id'])
            vals['code_externe'] = processus.code.upper() + self.env['ir.sequence'].next_by_code('prestation_code')
        res = super(account_prestation, self).create(vals)
        return res

    @api.constrains('code_externe')
    def _check_unique_initial_step(self):
        if self.code_externe != '/':
            prestations = self.env['account.prestation'].search([('id', '!=', self.id),
                                                                 ('code_externe', '=', self.code_externe)])
        if len(prestations) >= 1:
            raise Warning(_(u"Ce code existe déja!"))

    name = fields.Char(string=u'Description')
    code = fields.Char(string=u'Code', required=True)
    code_externe = fields.Char(required=True, default='/')
    active = fields.Boolean('Actif', default=True)
    processus_id = fields.Many2one('account.processus', string=u"Processus",required=True)
    marco_prestation_id = fields.Many2one('account.macro.prestation', string=u"Macro prestation")
    import_export = fields.Selection(
        [('import', 'Import'), ('export', 'Export')], 'Import/Export')
    phase_id = fields.Many2one('account.prestation.phase',string=u"Phase")
    prestation_attribute_a_id = fields.Many2one('prestation.attribute.a', string=u"Attribut de prestation A")
    prestation_attribute_b_id = fields.Many2one('prestation.attribute.b', string=u"Attribut de prestation B")
    prestation_attribute_c_id = fields.Many2one('prestation.attribute.c', string=u"Attribut de prestation C")
    prestation_attribute_d_id = fields.Many2one('prestation.attribute.d', string=u"Attribut de prestation D")
    prestation_attribute_e_id = fields.Many2one('prestation.attribute.e', string=u"Attribut de prestation E")

    prorata_type = fields.Selection(
        [('margin', 'Marge'), ('cost', 'Coût')], 'Prorata')
    prestation_ids = fields.Many2many('account.prestation','presta_prorata_rel','presta_id','prorata_id',string=u'Prestations cibles')
    prorata_processus_id = fields.Many2one('account.processus', string=u"Processus prorata")