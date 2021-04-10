# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


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