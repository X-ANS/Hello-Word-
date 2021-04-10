# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class PortnetOps(models.Model):
    _name = 'portnet.ops'

    name = fields.Char('Code',required=True)
    desc = fields.Char('Description',required=True)
    document_id = fields.Many2one('account.prestation', string=u'Document', required=True)
    code_externe = fields.Char(default='/')

    @api.model
    def create(self, vals):
        if not vals.get('code_externe', False) or vals['code_externe'] == '/':
            vals['code_externe'] = self.env['ir.sequence'].next_by_code('portnet_ops')
        res = super(PortnetOps, self).create(vals)
        return res

    @api.one
    @api.constrains('code_externe')
    def _check_ops_code_externe(self):
        if self.code_externe != '/':
            ops = self.env['portnet.ops'].search([('code_externe', '=', self.code_externe)])
        if len(ops) > 1:
            raise Warning(_(u"Ce code existe déja!"))


class PortnetDocOps(models.Model):
    _name = 'portnet.doc.ops'

    name = fields.Many2one('account.prestation', string=u'Prestation',required=True)
    num = fields.Float(string=u"Nombre d'opération",required=True)
    date = fields.Date(string=u"Date",required=True)
    op_id = fields.Many2one('portnet.ops',required=True,string=u'Opération')
    desc_op = fields.Char(related='op_id.desc',string=u'Description opération',readonly=True)


class PortnetMatrix(models.Model):
    _name = 'portnet.matrix'
    _rec_name = 'prestation_id'

    prestation_id = fields.Many2one('account.prestation', string=u'Document', required=True)
    op_id = fields.Many2one('portnet.ops', string=u'Opération', required=True,domain="[('document_id', '=', prestation_id)]")
    client_categ_ids = fields.Many2many('account.prestation', 'matrix_presta_rel',string=u'Cactégories clients',required=True)

    _sql_constraints = [
        ('name_op_id',
         'UNIQUE(op_id)',
         u"L'opération doit être unique!"),
    ]
