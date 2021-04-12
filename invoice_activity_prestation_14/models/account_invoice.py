# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    activity_id = fields.Many2one('account.activity', string=u'Activité')
    activity_type = fields.Selection(related='activity_id.type',string=u'type',store=True)
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    key_activity_id = fields.Many2one('key.activity', string=u'Clé activité')

    @api.constrains('activity_id', 'key_activity_id','prestation_id')
    def _check_activity(self):
        if self.activity_id and self.prestation_id and self.activity_id.type=='direct' and self.activity_id.prestation_ids:
            if self.prestation_id not in self.activity_id.prestation_ids:
                raise Warning(u"La prestation %s ne peut pas être associée à l'activité %s !"%(self.prestation_id.name,self.activity_id.name))
        if self.activity_id and self.key_activity_id:
            raise Warning(u"L'activité et la clé d'activité ne doivent pas être saisis en même temps!")
        if self.activity_id and self.account_id and self.account_id.activity_id and self.account_id.activity_id != self.activity_id:
            raise Warning(u"La seule valeur possible pour l'activité est %s (compte: %s)!"%(self.account_id.activity_id.name,self.account_id.code))
        if self.key_activity_id and self.account_id and self.account_id.key_activity_id and self.account_id.key_activity_id != self.key_activity_id:
            raise Warning(u"La seule valeur possible pour la clé d'activité est %s (compte: %s)!"%(self.account_id.key_activity_id.name,self.account_id.code))

    @api.onchange('activity_id')
    def on_change_activity(self):
        if self.activity_id:
            res = {}
            res['domain'] = {}
            if self.activity_id.type == 'direct' and self.activity_id.prestation_ids:
                if len(self.activity_id.prestation_ids) == 1:
                    self.prestation_id = self.activity_id.prestation_ids
                else:
                    self.prestation_id = False
                res['domain']['prestation_id'] = [('id', '=', self.activity_id.prestation_ids.ids)]
            else:
                self.prestation_id = False
            return res

    def onchange_account_id(self, product_id, partner_id, inv_type, fposition_id, account_id):
        res = super(AccountMoveLine, self).onchange_account_id(product_id, partner_id, inv_type, fposition_id, account_id)
        if not account_id:
            return {}
        unique_tax_ids = []
        activity_id = False
        key_activity_id = False
        res['domain'] = {}
        res['domain']['activity_id'] = [('id', '!=', False)]
        res['domain']['key_activity_id'] = [('id', '!=', False)]
        account = self.env['account.account'].browse(account_id)
        if not product_id:
            fpos = self.env['account.fiscal.position'].browse(fposition_id)
            unique_tax_ids = fpos.map_tax(account.tax_ids).ids
        else:
            product_change_result = self.product_id_change(product_id, False, type=inv_type,
                                                           partner_id=partner_id, fposition_id=fposition_id,
                                                           company_id=account.company_id.id)
            if 'invoice_line_tax_id' in product_change_result.get('value', {}):
                unique_tax_ids = product_change_result['value']['invoice_line_tax_id']
        if account.activity_id:
            activity_id=account.activity_id.id
            res['domain']['activity_id'] = [('id', '=', activity_id)]
        if account.key_activity_id:
            key_activity_id=account.key_activity_id.id
            res['domain']['key_activity_id'] = [('id', '=', key_activity_id)]
        res['value'] = {'invoice_line_tax_id': unique_tax_ids, 'activity_id':activity_id, 'key_activity_id':key_activity_id}
        print('reeeeeeeee', res, activity_id)

        return res

    @api.model
    def move_line_get_item(self, line):
        vals = super(AccountMoveLine,self).move_line_get_item(line)
        if line.activity_id:
            vals['activity_id']=line.activity_id.id
        if line.prestation_id:
            vals['prestation_id']=line.prestation_id.id
        if line.key_activity_id:
            vals['key_activity_id']=line.key_activity_id.id
        return vals


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def line_get_convert(self, line, part, date):
        vals = super(AccountMove,self).line_get_convert(line,part,date)
        vals['activity_id']= line.get('activity_id',False)
        vals['prestation_id']= line.get('prestation_id',False)
        vals['key_activity_id']= line.get('key_activity_id',False)
        return vals

    def action_move_create(self):
        for inv in self:
            if inv.type in ('in_invoice', 'in_refund') and any((not l.activity_id and not l.key_activity_id ) or not l.account_analytic_id for l in inv.invoice_line):
                raise ValidationError(u"Une ligne de cette facture n'a pas de compte analytique ou ni activité ni clé d'activité!")
        res = super(AccountMove, self).action_move_create()
        return res
