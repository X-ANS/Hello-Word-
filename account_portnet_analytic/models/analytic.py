# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, except_orm, ValidationError


class account_activity(models.Model):
    _name = 'account.activity'
    _inherit = ['mail.thread']
    _rec_name = 'code'
    _order = 'len_process'

    def name_get(self):
        return [(act.id, act.name) for act in self]

    name = fields.Char(string=u'Description', required=True)
    code = fields.Char(string=u'Code', required=True)
    active = fields.Boolean('Actif', default=True)
    processus_ids = fields.Many2many('account.processus', string='Processus', required=True)
    type = fields.Selection(
        [('direct', 'Direct'), ('indirect', 'Indirect'), ('prorata', 'Prorata'), ('manday', 'Manday')], 'Type',
        required=True)
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
    processus_id = fields.Many2one('account.processus', string=u"Processus", required=True)
    marco_prestation_id = fields.Many2one('account.macro.prestation', string=u"Macro prestation")
    import_export = fields.Selection(
        [('import', 'Import'), ('export', 'Export')], 'Import/Export')
    phase_id = fields.Many2one('account.prestation.phase', string=u"Phase")
    prestation_attribute_a_id = fields.Many2one('prestation.attribute.a', string=u"Attribut de prestation A")
    prestation_attribute_b_id = fields.Many2one('prestation.attribute.b', string=u"Attribut de prestation B")
    prestation_attribute_c_id = fields.Many2one('prestation.attribute.c', string=u"Attribut de prestation C")
    prestation_attribute_d_id = fields.Many2one('prestation.attribute.d', string=u"Attribut de prestation D")
    prestation_attribute_e_id = fields.Many2one('prestation.attribute.e', string=u"Attribut de prestation E")

    prorata_type = fields.Selection(
        [('margin', 'Marge'), ('cost', 'Coût')], 'Prorata')
    prestation_ids = fields.Many2many('account.prestation', 'presta_prorata_rel', 'presta_id', 'prorata_id',
                                      string=u'Prestations cibles')
    prorata_processus_id = fields.Many2one('account.processus', string=u"Processus prorata")


class account_processus(models.Model):
    _name = 'account.processus'
    _rec_name = 'code'

    name = fields.Char(string=u'Description', required=True)
    code = fields.Char(string=u'Code', required=True)
    tax_exclude = fields.Boolean(string=u"Exclure prestations avec déficit")


class activity_attribute_a(models.Model):
    _name = 'activity.attribute.a'
    _description = u"Attribut d'Activité A"

    name = fields.Char(string=u'Description')


class activity_attribute_b(models.Model):
    _name = 'activity.attribute.b'
    _description = u"Attribut d'Activité B"

    name = fields.Char(string=u'Description')


class activity_attribute_c(models.Model):
    _name = 'activity.attribute.c'
    _description = u"Attribut d'Activité C"

    name = fields.Char(string=u'Description')


class activity_attribute_d(models.Model):
    _name = 'activity.attribute.d'
    _description = u"Attribut d'Activité D"

    name = fields.Char(string=u'Description')


class activity_attribute_e(models.Model):
    _name = 'activity.attribute.e'
    _description = u"Attribut d'Activité E"

    name = fields.Char(string=u'Description')


class prestation_attribute_a(models.Model):
    _name = 'prestation.attribute.a'
    _description = u"Attribut de prestation A"

    name = fields.Char(string=u'Description')


class prestation_attribute_b(models.Model):
    _name = 'prestation.attribute.b'
    _description = u"Attribut de prestation B"

    name = fields.Char(string=u'Description')


class prestation_attribute_c(models.Model):
    _name = 'prestation.attribute.c'
    _description = u"Attribut de prestation C"

    name = fields.Char(string=u'Description')


class prestation_attribute_d(models.Model):
    _name = 'prestation.attribute.d'
    _description = u"Attribut de prestation D"

    name = fields.Char(string=u'Description')


class prestation_attribute_e(models.Model):
    _name = 'prestation.attribute.e'
    _description = u"Attribut de prestation E"

    name = fields.Char(string=u'Description')


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


class key_activity(models.Model):
    _name = 'key.activity'
    _inherit = ['mail.thread']

    name = fields.Char(string=u'Description',required=True)
    code = fields.Char(string=u'Code',required=True)
    active = fields.Boolean('Actif', default=True)
    key_activity_lines = fields.One2many('key.activity.line','key_activity_id',string=u'Valeurs de la clé')

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