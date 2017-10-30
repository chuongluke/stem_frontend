# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class stem_register_parent(models.Model):
    _name = 'stem.register_parent'

    token = fields.Char(copy=False)
    parent_id = fields.Many2one('res.partner')
    expiration = fields.Datetime(copy=False)
    student_child_id = fields.Many2one('op.student')
