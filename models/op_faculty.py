import logging
from odoo import http
from odoo import models, fields, api, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class OpFaculty(models.Model):
	_inherit = 'op.faculty'

	status = fields.Selection([('unapprove', 'Unapprove'), ('approve', 'Approve')], string='Status', default='unapprove')


	@api.multi
	def action_approve(self):
		for record in self:
			record.status = 'approve'

			uid = record.partner_id.user_id.id
			user = self.env['res.users'].search([('id', '=', uid)])
			groups_faculty = self.env['res.groups'].search([('name', 'ilike', 'Faculty')])
			if groups_faculty:
				for x in groups_faculty:
					user.write({'groups_id': [(4, x.id, 0)]})

			template = http.request.env.ref('stem_frontend_theme.faculty_mail_template')
			self.env['mail.template'].sudo().browse(template.id).send_mail(record.id, force_send=True)