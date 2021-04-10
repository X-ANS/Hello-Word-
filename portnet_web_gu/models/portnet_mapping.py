# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class donnees_agregees(models.Model):
    _name = 'donnees.agregees'

    type_document = fields.Char()
    code_odoo = fields.Char(string='Code odoo du document')
    code_operation = fields.Char(string='Code odoo opération')
    operation = fields.Char(string="Description")
    nombre_operation = fields.Float()
    date_operation = fields.Date()


class donnees_detaillees(models.Model):
    _name = 'donnees.detaillees'

    # cible portnet.client

    code_odoo = fields.Char('Code catégorie client')
    operateur = fields.Char('Compte client')
    code_client = fields.Char('Code client')
    nombre_operation = fields.Float()
    date_operation = fields.Date()


class donnees_doc_dematerialises(models.Model):
    _name = 'donnees.doc.dematerialises'

    document = fields.Char('Document dématerialisé')
    code_document = fields.Char('Code odoo document')
    quantite = fields.Float()
    date = fields.Date()