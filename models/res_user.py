# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class res_users(models.Model):
	_inherit = 'res.users'

	birthday = fields.Date('Birthday')
	gender = fields.Selection(string='Gender', 
		selection=[('male', 'Male'), ('female', 'Female')])