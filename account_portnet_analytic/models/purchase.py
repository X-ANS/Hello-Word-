# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    type_opration = fields.Selection([('appel_offres','Appel d`offres'),('bons_de_comman','Bons de Commande'),('contrat_cadre','Contrat cadre')],
                              'Type d`opération', tracking=True, copy=False)
    n_oprations = fields.Char(string='N Opération')
    object_t = fields.Char(string='Object')
    ordering_date = fields.Date(string="Date de commande planifiée", tracking=True)
    schedule_date = fields.Date(string='Date prévue de livraison', index=True, help="The expected and scheduled delivery date where all the products are received", tracking=True)


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"


    # object_t = fields.Char(string='Object')
    # object_t = fields.Char(string='Object')
    # object_t = fields.Char(string='Object')