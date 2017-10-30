# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
import lxml
import requests
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers

from datetime import datetime

from odoo import http, modules, SUPERUSER_ID, tools, _
from odoo.addons.website.models.website import slug
from odoo.addons.web.controllers.main import binary_content
from odoo.http import request


class WebsiteForums(http.Controller):
    @http.route('/forum/<model("forum.forum"):forum>/user/<model("res.users"):user>/saved', type='http', auth="user", methods=['POST'], website=True)
    def save_edited_profiles(self, forum, user, **kwargs):
        values = {
            'name': kwargs.get('name'),
            'website': kwargs.get('website'),
            'email': kwargs.get('email'),
            'city': kwargs.get('city'),
            'country_id': int(kwargs.get('country')) if kwargs.get('country') else False,
            'website_description': kwargs.get('description'),
        }

        if 'clear_image' in kwargs:
            values['image'] = False
        elif kwargs.get('ufile'):
            image = kwargs.get('ufile').read()
            values['image'] = base64.b64encode(image)

        if request.uid == user.id:  # the controller allows to edit only its own privacy settings; use partner management for other cases
            values['website_published'] = kwargs.get('website_published') == 'True'
        user.write(values)
        return werkzeug.utils.redirect("/forum/%s/user/%d" % (slug(forum), user.id))

