# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class account_account(models.Model):
    _inherit = 'account.account'

    activity_id = fields.Many2one('account.activity', string=u'Activité')
    key_activity_id = fields.Many2one('key.activity', string=u'Clé activité')

    @api.one
    @api.constrains('activity_id', 'key_activity_id')
    def _check_activity(self):
        if self.activity_id and self.key_activity_id:
            raise Warning(_(u"L'activité et la clé d'activité ne doivent pas être saisis en même temps!"))


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    activity_id = fields.Many2one('account.activity', string=u'Activité')
    activity_type = fields.Selection(related='activity_id.type', string=u'type', store=True)
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    key_activity_id = fields.Many2one('key.activity', string=u'Clé activité')

    @api.one
    @api.constrains('activity_id', 'key_activity_id', 'prestation_id')
    def _check_activity(self):
        if self.activity_id and self.key_activity_id:
            raise Warning(u"L'activité et la clé d'activité ne doivent pas être saisis en même temps!")
        if self.activity_id and self.account_id and self.account_id.activity_id and self.account_id.activity_id != self.activity_id:
            raise Warning(u"La seule valeur possible pour l'activité est %s (compte: %s)!" % (
            self.account_id.activity_id.name, self.account_id.code))
        if self.key_activity_id and self.account_id and self.account_id.key_activity_id and self.account_id.key_activity_id != self.key_activity_id:
            raise Warning(u"La seule valeur possible pour la clé d'activité est %s (compte: %s)!" % (
            self.account_id.key_activity_id.name, self.account_id.code))

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

    @api.multi
    def onchange_account_id(self, account_id, partner_id):

        res = super(account_move_line, self).onchange_account_id(account_id=account_id, partner_id=partner_id)

        if account_id:

            account = self.env['account.account'].browse(account_id)
            # res = {}
            res['domain'] = {}
            if account.activity_id:
                res['value']['activity_id'] = account.activity_id.id
                res['domain']['activity_id'] = [('id', '=', account.activity_id.id)]
            elif account.key_activity_id:
                res['value']['key_activity_id'] = account.key_activity_id.id
                res['domain']['key_activity_id'] = [('id', '=', account.key_activity_id.id)]
            else:
                res['domain']['activity_id'] = [('id', '!=', False)]
                res['domain']['key_activity_id'] = [('id', '!=', False)]
                res['value']['activity_id'] = False
                res['value']['prestation_id'] = False
                res['value']['key_activity_id'] = False
            return res

    @api.multi
    def create_analytic_lines(self):
        acc_ana_line_obj = self.env['account.analytic.line']
        for obj_line in self:
            if obj_line.analytic_lines:
                obj_line.analytic_lines.unlink()
            if obj_line.analytic_account_id:
                if not obj_line.journal_id.analytic_journal_id:
                    raise except_orm(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (obj_line.journal_id.name, ))
                if obj_line.key_activity_id:
                   for line in  obj_line.key_activity_id.key_activity_lines:
                       if line.prestation_id:
                           vals_line = self._prepare_analytic_line(obj_line)
                           vals_line['unit_amount'] = vals_line['unit_amount']*line.value/100.0
                           vals_line['amount'] = vals_line['amount']*line.value/100.0
                           vals_line['activity_id'] = line.activity_id.id
                           vals_line['prestation_id'] = line.prestation_id.id
                           acc_ana_line_obj.create(vals_line)
                       elif line.key_id:
                            key_val_ids = self.env['analytic.key.value'].read_group([('analytic_key_id', '=', line.key_id.id)]
                                                                                    , ['prestation_id', 'value'],
                                                                                    ['prestation_id'])
                            key_val_dict = {}
                            for val in key_val_ids:
                                key_val_dict[val['prestation_id'][0]] = val['value']
                            sum_ratio = sum(key_val_dict.values())
                            for presta in key_val_dict:
                                ratio = round(key_val_dict[presta] / (sum_ratio or 1.0), 2)
                                vals_line = self._prepare_analytic_line(obj_line)
                                vals_line['unit_amount'] = ratio * vals_line['unit_amount'] * line.value / 100.0
                                vals_line['amount'] = ratio * vals_line['amount'] * line.value / 100.0
                                vals_line['activity_id'] = line.activity_id.id
                                vals_line['prestation_id'] = presta
                                acc_ana_line_obj.create(vals_line)
                       else:
                           vals_line = self._prepare_analytic_line(obj_line)
                           vals_line['unit_amount'] = vals_line['unit_amount'] * line.value / 100.0
                           vals_line['amount'] = vals_line['amount'] * line.value / 100.0
                           vals_line['activity_id'] = line.activity_id.id
                           acc_ana_line_obj.create(vals_line)
                else:
                    vals_line = self._prepare_analytic_line(obj_line)
                    acc_ana_line_obj.create(vals_line)
        return True


    @api.model
    def _prepare_analytic_line(self,obj_line):
        return {'name': obj_line.name,
                'date': obj_line.date,
                'account_id': obj_line.analytic_account_id.id,
                'activity_id':obj_line.activity_id.id,
                'prestation_id':obj_line.prestation_id.id,
                'unit_amount': obj_line.quantity,
                'product_id': obj_line.product_id and obj_line.product_id.id or False,
                'product_uom_id': obj_line.product_uom_id and obj_line.product_uom_id.id or False,
                'amount': (obj_line.credit or  0.0) - (obj_line.debit or 0.0),
                'general_account_id': obj_line.account_id.id,
                'journal_id': obj_line.journal_id.analytic_journal_id.id,
                'ref': obj_line.ref,
                'move_id': obj_line.id,
                'user_id': obj_line.invoice.user_id.id or self.env.user.id,
               }


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    activity_id = fields.Many2one('account.activity', string=u'Activité')
    prestation_id = fields.Many2one('account.prestation', string=u'Prestation')
    prestation_pro_id = fields.Many2one(related='prestation_id.processus_id', string=u'Processus',store=True)
    activity_type = fields.Selection(related='activity_id.type', string=u'type', store=True)


class account_move(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        for rec in self:
           for line in rec.line_id:
               if line.account_id.code.startswith('6') and( (not line.activity_id and not line.key_activity_id ) or not line.analytic_account_id ):
                raise ValidationError(
                    u"Une écriture de charge n'a pas de compte analytique ou ni activité ni clé d'activité!")
        res = super(account_move, self).post()
        return res
