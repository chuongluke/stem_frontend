# -*- coding: utf-8 -*-
import json
import uuid
import werkzeug.utils
import base64
import logging
import random
import requests
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers
from datetime import datetime, timedelta

from odoo import _, http, fields,modules, SUPERUSER_ID, tools
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import Home
from odoo.addons.website.models.website import slug
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import binary_content
from odoo.http import request
PPG = 2
PPR = 4
_logger = logging.getLogger(__name__)

try:
    from validate_email import validate_email
except ImportError:
    _logger.debug("Cannot import `validate_email`.")

class Stem(http.Controller):
    def get_menu_data(self):
        parent = http.request.env['op.parent'].sudo().search([('name', '=', http.request.env.user.partner_id.id)], limit=1)
        
        student = http.request.env['op.student'].sudo().search([('partner_id', '=', http.request.env.user.partner_id.id)], limit=1)
        student_id = [x.id for x in student]
        parent_child_sm= http.request.env['op.parent'].sudo().search([('student_ids.id', 'in' ,student_id)])
        parent_child_sm_id=[x.name for x in parent_child_sm]
        parent_child_sm_id_2=[x.id for x in parent_child_sm_id]
        parent_child_rg = http.request.env['stem.register_parent'].sudo().search([('student_child_id', 'in' ,student_id) ,('parent_id', 'not in' ,parent_child_sm_id_2)])
        parent_child = [x.parent_id for x in parent_child_rg]
    
                                                             
                           
        online_free_courses = http.request.env['op.course'].sudo().search([('online_course', '=', True), ('type', '=', 'free')], limit=3, order='create_date desc')

        online_paid_courses = http.request.env['op.course'].sudo().search(                
                [('online_course', '=', True), ('type', '=', 'paid')], limit=3, order='create_date desc')


        my_channels = http.request.env['mail.channel'].sudo().search([('channel_partner_ids', 'in', [http.request.env.user.partner_id.id])],limit=10, order='__last_update asc')

        enrollments = http.request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', http.request.env.uid),
            ('state', 'in', ['in_progress', 'done'])])
        my_courses = []
        if enrollments:
            my_courses = self.my_course_details(enrollments)

        forums = http.request.env['forum.forum'].sudo().search([])
        forum = http.request.env['forum.forum'].sudo().search([('id', '=', 2)])

        posts = http.request.env['blog.post'].sudo().search([('website_published', '=', True)])

        all_courses = http.request.env['op.course'].sudo().search([])

        events = http.request.env['event.event'].sudo().search([])

        #course_porpular = http.request.env['rec.cu.by.predef'].sudo().search([])
        course_porpular = []

        course_porpular_ids = [x.course_id.id for x in course_porpular]

        porpular_courses = http.request.env['op.course'].sudo().search([('id', 'in', course_porpular_ids)], limit=9, order='create_date desc')
        
        forum_posts = http.request.env['forum.post'].sudo().search([('parent_id', '=', False),('forum_id', '=', 2)], order='create_date desc')
        
        my_question = request.env['forum.post'].search([
                ('parent_id', '=', False),
                ('forum_id', '=', 2), ('create_uid', '=', http.request.env.user.id)],order='relevancy desc')
                
        questions = request.env['forum.post'].search([
                ('parent_id', '=', False),
                ('forum_id', '=', 2)], limit=5,order='create_date desc')

        return {
            'needaction_inbox_counterz': http.request.env['res.partner'].get_needaction_count(),
            'parent': parent,
            'online_free_courses': online_free_courses,
            'my_channels': my_channels,
            'my_courses': my_courses,
            'my_questions':my_question,
            'questions':questions,
            'forums': forums,
            'forum': forum,
            'posts': posts,
            'online_paid_courses': online_paid_courses, 
            'course_porpular': porpular_courses,
            'events': events, 
            'all_courses': all_courses,
            'forum_posts': forum_posts,
            'parent_child': parent_child,
            'parent_child_sm':parent_child_sm_id
        }

    @http.route('/home', auth='user', website=True)
    def home(self, **kw):
        data = self.get_menu_data()

        #online_free_courses
        online_free_courses = http.request.env['op.course'].sudo().search(
            [('online_course', '=', True), ('type', '=', 'free')], limit=3, order='create_date desc')
        data['online_free_courses'] = online_free_courses
        

        #my courses
        enrollments = http.request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', http.request.env.uid),
            ('state', 'in', ['in_progress', 'done'])])
        if enrollments:
            data.update(self.my_course_details(enrollments))
        #my courses
        
        return http.request.render('stem_frontend_theme.stem_profile', data)

    @http.route('/googleb90fcbde0047b306.html', auth='public')
    def google_html(self):
        return 'google-site-verification: googleb90fcbde0047b306.html'

    @http.route('/blog', auth='public',website=True)
    def view_blog(self):
        return http.request.redirect('/blog/cong-ong-stem-1')

    @http.route('/forum', auth='public',website=True)
    def view_forum(self):
        return http.request.redirect('/forum/stem-forum-2')
    
    @http.route('/home/my-courses', auth='user', website=True)
    def my_courses(self, **kw):
        data = self.get_menu_data()

        enrollments = http.request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', http.request.env.uid),
            ('state', 'in', ['in_progress', 'done'])])
        if enrollments:
            data.update(self.my_course_details(enrollments))

        return http.request.render('stem_frontend_theme.stem_my_courses', data)

    def my_course_details(self, enrollments):
        courses = []
        for en in enrollments:
            completed_percentage = 0
            if en and en.course_id.training_material > 0:
                viewed_material = http.request.env[
                    'op.course.enrollment.material'].sudo().search_count([   
                        ('completed', '=', True),
                        ('course_id', '=', en.course_id.id),
                        ('enrollment_id', '=', en.id)
                    ])
                completed_percentage = (viewed_material * 100) / en.course_id.training_material
            courses.append({
                'course': en.course_id,
                'enrolled': en.state in ['in_progress', 'done'] and True or False,
                'completed_percentage': completed_percentage, 
            })
        return {
            'my_courses': courses
        }

    @http.route('/home/register_teacher', auth='user', methods=['POST'], website=True)
    def register_teacher(self, **post):
        name = post.get('name')
        middle_name = post.get('middle_name')
        last_name = post.get('last_name')
        gender = post.get('gender')
        phone = post.get('phone')
        email = post.get('email')
        birth_date = post.get('birth_date')
        
        #birth_date = birth_date.strftime('%Y-%m-%d')
        
        faculty = http.request.env['op.faculty'].search([('user_id', '=', http.request.env.uid)])
        if not faculty:
            fac = http.request.env['op.faculty'].sudo().create({
                'partner_id': http.request.env.user.partner_id.id,
                'last_name': last_name,
                'gender': gender,
                'phone': phone,
                'email': email,
                'birth_date': birth_date,
                'status': 'unapprove'
            })

            if fac:
                vals = {
                    'name': name + ' ' + (middle_name or '') +
                    ' ' + last_name,
                    'country_id': fac.nationality.id,
                    'gender': gender,
                    'address_home_id': fac.partner_id.id
                }
                emp_id = http.request.env['hr.employee'].sudo().create(vals)
                fac.write({'emp_id': emp_id.id})
                fac.partner_id.write({'user_id': http.request.env.uid, 'supplier': True, 'employee': True})

        return http.request.render('stem_frontend_theme.stem_alert', {
            'message': 'Đăng ký thành công, vui lòng chờ xác nhận của quản lý hệ.',
            'type': 'success'
        })

    def random_token(self):
        # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))

    def now(self, **kwargs):
        dt = datetime.now() + timedelta(**kwargs)
        return fields.Datetime.to_string(dt)

    @http.route('/register/parent', type='http', auth="user", methods=['POST'], website=True)
    def register_parent(self, **kw):
        sids = kw.get('student_ids')

        if sids:
            student_ids = [int(i) for i in sids.split(',')]
            template = http.request.env.ref('stem_frontend_theme.register_parent_template')

            for student_id in student_ids:
                token = self.random_token()
                parent_id = http.request.env.user.partner_id.id
                expiration = self.now(days=+1)
                student_child_id = student_id

                registered = http.request.env['stem.register_parent'].sudo().create({
                    'token': token,
                    'parent_id': parent_id,
                    'expiration': expiration,
                    'student_child_id': student_id
                })

                http.request.env['mail.template'].sudo().browse(template.id).send_mail(registered.id, force_send=True)
        return http.request.render('stem_frontend_theme.stem_alert', {
            'message': 'Đăng ký thành công',
            'type': 'success'
        })

            # res = http.request.env['op.parent'].sudo().create({
            #     'name': http.request.env.user.partner_id.id,
            #     'student_ids': [(6, 0, student_ids)]
            # })

        #return http.request.redirect('/home')

    @http.route('/confirm/parent', type='http', auth='public', website=True)
    def confirm_parent(self, **kw):
        token = kw.get('token')
        message = 'Mã xác thực đã hết hạn hoặc không tồn tại'
        alert_type ='danger'
        if token:
            registered = http.request.env['stem.register_parent'].sudo().search([('token', '=', token)], limit=1)
            dt = self.now()
            if registered and token == registered.token and dt <= registered.expiration:
                parent = http.request.env['op.parent'].sudo().search([('name', '=', registered.parent_id.id)], limit=1)
                if parent:
                    parent.write({
                        'student_ids': [(4, registered.student_child_id.id, 0)]
                    })
                else:
                    http.request.env['op.parent'].sudo().create({
                        'name': registered.parent_id.id,
                        'student_ids': [(6, 0, [registered.student_child_id.id])]
                    })
                message = 'Xác nhận thành công'
                alert_type = 'success'

        return http.request.render('stem_frontend_theme.stem_alert', {
            'message': message,
            'type': alert_type
        })

    
    @http.route('/confirm/parentz', type='http', auth='user', method=['POST'],website=True)
    def confirm_parentz(self, **kw):
        token = kw.get('token')
        if token:
            student = http.request.env['op.student'].sudo().search([('partner_id', '=', http.request.env.user.partner_id.id)], limit=1)
            student_id = [x.id for x in student]
            parent_child_sm= http.request.env['op.parent'].sudo().search([('student_ids.id', 'in' ,student_id)])
            parent_child_sm_id=[x.name for x in parent_child_sm]
            parent_child_sm_id_2=[x.id for x in parent_child_sm_id]
            parent_child_rg = http.request.env['stem.register_parent'].sudo().search([('student_child_id', 'in' ,student_id) ,('parent_id', 'not in' ,parent_child_sm_id_2)])
            for x in range(1, len(parent_child_rg)+1):
                val = kw.get(str(x))
                if val:       
                    http.request.env['op.parent'].sudo().create({
                            'name': parent_child_rg[x-1].parent_id.id,
                            'student_ids': [(6, 0,student_id)]
                        })
            
            parent_child_rg.unlink()
    return http.request.redirect('/home')
            
        
    @http.route('/home/my-blogs', auth='user', website=True)
    def my_blogs(self, **kw):
        data = self.get_menu_data()
        return http.request.render('stem_frontend_theme.stem_my_blogs', data)

    @http.route('/home/my-mes', auth='user', website=True)
    def my_mes(self, **kw):
        data = self.get_menu_data()
        my_channels = http.request.env['mail.channel'].sudo().search(
            [('channel_partner_ids', 'in', [http.request.env.user.partner_id.id])],limit=10, order='__last_update asc')
        #_logger.info("my_channels len: " + str(len(my_channels)))
        #for c in my_channels:
        #    _logger.info("my_channels: " + c.public)
        data['partner_id'] = http.request.env.user.partner_id.id
        data['my_channels'] = my_channels
        # for c in data['my_channels']:
        #     body = c.message_ids[0].body
        #     body = self.replaceTag(body)
        #     c['first_body'] = body
        #     _logger.info("body: " + body+"--c['first_body']--"+c['first_body'])

        return http.request.render('stem_frontend_theme.stem_my_mes', data)

    def replaceTag(self, enrollments):
        num = re.sub(r"(<([^>]+)>)", '', enrollments)
        return num

    @http.route('/home/get_student', auth='public', type='http', csrf=False, website=True)
    def get_student(self, **kw):
        start = int(kw.get('start'))
        length = int(kw.get('length'))
        search = kw.get('search[value]')

        total_count = http.request.env['op.student'].sudo().search_count([])
        filtered_count = http.request.env['op.student'].sudo().search_count(['|', ('partner_id.email', 'ilike', search), ('partner_id.name', 'ilike', search)])
        students = http.request.env['op.student'].sudo().search(['|', ('partner_id.email', 'ilike', search), ('partner_id.name', 'ilike', search)], offset=start, limit=length)

        data = []
        for student in students:
            data.append({
                'DT_RowId': student.id,
                'action': '<input type="checkbox"/>',
                'email': student.partner_id.email,
                'name': student.name
            })

        result = {
            'recordsTotal': total_count,
            'recordsFiltered': filtered_count,
            'data': data
        }

        return str(json.dumps(result))

    @http.route('/home/my-child/<int:student_id>', auth='user', website=True)
    def my_child(self, student_id=0):
        data = self.get_menu_data()
        parent = data['parent']
        if parent:
            student_ids = [s for s in parent.student_ids if s.id == student_id]
            if student_ids:
                child = student_ids[0]
                student_user = http.request.env['res.users'].sudo().search([('partner_id', '=', child.partner_id.id)], limit=1)
                student_user_id = student_user.id

                enrollments = http.request.env['op.course.enrollment'].sudo().search(
                    [('user_id', '=', student_user_id),
                    ('state', 'in', ['in_progress', 'done'])])
                if enrollments:
                    data.update(self.my_course_details(enrollments))

                data['child'] = child

                return http.request.render('stem_frontend_theme.stem_my_child_courses', data)
            else:
                return http.request.redirect('/home')
        else:
            return http.request.redirect('/home')

    @http.route('/home/get_messages_by_channel', auth='public', type='http', csrf=False, website=True)
    def get_messages_by_channel(self, **kw):
        data = self.get_menu_data()
        channel_id = int(kw.get('channel_id'))

        messages = http.request.env['mail.message'].sudo().search([('res_id', '=', channel_id), ('model', '=', 'mail.channel')], order='create_date desc')
        data['messages']=messages
        #result = []
        # for m in messages:
        #     result.append({
        #         'id': m.id,
        #         'body': m.body,
        #         'author_name': m.author_id.name
        #     })

        return http.request.render('stem_frontend_theme.stem_my_mes_detail',  data)


    @http.route(['''/course/register-course/<model("op.course"):course>'''],
                type='http', auth="user", website=True)
    def register_course(self, course, **kwargs):
        course = http.request.env['op.course'].sudo().browse([course.id])
        faculty = http.request.env['op.faculty'].search([('user_id', '=', http.request.env.uid)])
        if course and faculty:
            course.write({'faculty_ids': [(4, faculty.id, 0)]})

        sections = http.request.env['op.course.section'].sudo().search(
            [('course_id', '=', course.id)], order='sequence asc')

        enrollment = http.request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', http.request.env.uid),
             ('course_id', '=', course.id),
             ('state', 'in', ['in_progress', 'done'])])

        completed_percentage = enrollment and enrollment.completed_percentage or 0

        ratings = http.request.env['rating.rating'].sudo().search(
            [('message_id', 'in', course.website_message_ids.ids)])
        rating_message_values = dict(
            [(record.message_id.id, record.rating) for record in ratings])
        rating_course = course.rating_get_stats()
        values = {
            'course': course,
            'enrolled': enrollment and True or False,
            'completed_percentage': completed_percentage,
            'sections': sections,
            'user': http.request.env.user,
            'is_public_user': http.request.env.user == http.request.website.user_id,
            'rating_message_values': rating_message_values,
            'rating_course': rating_course,
            'message': 'Đăng ký thành công.'
        }
        return http.request.render('openeducat_lms.course_detail', values)



    @http.route(['/searchz', '/searchz/page/<int:page>'], type='http', auth="public", website=True)
    def searchz(self, search='', page=0, ppg=False, **post):
        data = self.get_menu_data()
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        url = '/searchz'

        domain_cource_default = [('online_course', '=', True)]

        if search:
            post["search"] = search

            for srch in search.split(" "):
                domain_cource_default += [('name', 'ilike', srch)]

        course_domain = domain_cource_default + [('state', '=', 'open')]

        

        domain_post_default = [('website_published', '=', True)]

        if search:
            post["search"] = search

            for srch in search.split(" "):
                domain_post_default += [('name', 'ilike', srch)]

        domain_partner_default = []

        if search:
            post["search"] = search

            for srch in search.split(" "):
                domain_partner_default += [('name', 'ilike', srch)]

        posts = http.request.env['blog.post'].sudo().search(domain_post_default)
        courses = http.request.env['op.course'].sudo().search(course_domain)
        partners = http.request.env['res.partner'].sudo().search(domain_partner_default)
        total_count_courses = len(courses)
        total_count_posts =  len(posts)
        total_count_partners = len(partners)

        pager_courses = http.request.website.pager(
            url=url, total=total_count_courses, page=page, step=ppg, scope=7,
            url_args=post)

        pager_posts = http.request.website.pager(
            url=url, total=total_count_posts, page=page, step=ppg, scope=7,
            url_args=post)

        pager_partners = http.request.website.pager(
            url=url, total=total_count_partners, page=page, step=ppg, scope=7,
            url_args=post)
        

        all_search_idc = [x.id for x in courses]
        all_search_idp = [x.id for x in posts]
        all_search_idpn = [x.id for x in partners]
        all_search_courses = http.request.env['op.course'].sudo().search([('id', 'in', all_search_idc)], limit=ppg, offset=pager_courses['offset'])
        all_search_posts = http.request.env['blog.post'].sudo().search([('id', 'in', all_search_idp)], limit=ppg, offset=pager_posts['offset'])
        all_search_partners = http.request.env['res.partner'].sudo().search([('id', 'in', all_search_idpn)], limit=ppg, offset=pager_partners['offset'])

        values = {
            'search': search,
            'pager': pager_courses,
            'pager_posts': pager_posts,
            'total_count_courses': total_count_courses,
            'all_search_courses': all_search_courses,
            'total_count_posts': total_count_posts,
            'all_search_posts': all_search_posts,
            'total_count_partners': total_count_partners,
            'all_search_partners': all_search_partners,
            'rows': 3
        }
        
        data.update(values)

        return http.request.render("stem_frontend_theme.search_results", data)


    @http.route('/home/my-courses-teach', type='http', auth="public", website=True)
    def my_courses_teach(self, page=0, ppg=False, **post):
        data = self.get_menu_data()
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = 4
            post["ppg"] = ppg
        else:
            ppg = 4

        url = '/home/my-courses-teach'

        partner_id = http.request.env.user.partner_id.id;
        facultys = http.request.env['op.faculty'].sudo().search([('partner_id', '=', partner_id)])

        all_faculty_id = [x.id for x in facultys]

        course_domain = [('online_course', '=', True), ('state', '=', 'open'), ('faculty_ids', 'in', all_faculty_id)]

        courses = http.request.env['op.course'].sudo().search(course_domain)
        total_count = len(courses)

        pager = http.request.website.pager(
            url=url, total=total_count, page=page, step=ppg, scope=7,
            url_args=post)
        

        all_courses_id = [x.id for x in courses]
        all_courses_teach = http.request.env['op.course'].sudo().search([('id', 'in', all_courses_id)], limit=ppg, offset=pager['offset'])

        values = {
            'pager': pager,
            'total_count': total_count,
            'all_courses_teach': all_courses_teach,
            'rows': 3
        }
        
        data.update(values)

        return http.request.render("stem_frontend_theme.my_courses_teach", data)


    @http.route('/ask', type='http', auth="public", website=True, csrf=False)
    def add_post(self, **kw):
        # data = self.get_menu_data()
        name = kw.get('questionname')
        content = kw.get('questioncontent')
        
        if name:
            post = http.request.env['forum.post'].sudo().create({
                'name': name,
                'plain_content': name,
                'post_type': 'question',
                'content': content,
                'create_uid': http.request.env.uid,
                'write_uid': http.request.env.uid,
                'forum_id': 2,
                'write_date': self.now(days=+1),
                'create_date': self.now(days=+1)
            })

        # message = "Câu hỏi của bạn '"+ name +"'."
        # values = {
        #     'message': message
        # }

        # data.update(values)

        return http.request.redirect('/forum/stem-forum-2')


    @http.route('''/profile/<int:id>''', type='http',
                auth="public", website=True)
    def profile(self, id, **kw):
        partner = http.request.env['res.partner'].sudo().browse(id);
        if partner and partner.id == http.request.env.user.partner_id.id:
            return http.request.redirect('/home')
        else:
            return http.request.redirect('/profile/' + str(id) + '/blogs')
            # return http.request.render('stem_frontend_theme.stem_user_profile', {
            #     'partner': partner
            # })

    @http.route('''/profile/<int:id>/blogs''', type='http',
                auth="public", website=True)
    def profile_blogs(self, id, **kw):
        partner = http.request.env['res.partner'].sudo().browse(id);
        if partner and partner.id == http.request.env.user.partner_id.id:
            return http.request.redirect('/home/my-blogs')
        else:
            return http.request.render('stem_frontend_theme.stem_profile_blogs', {
                'partner': partner
            })

    @http.route('''/profile/<int:id>/courses''', type='http',
                auth="public", website=True)
    def profile_courses(self, id, **kw):
        partner = http.request.env['res.partner'].sudo().browse(id);
        if partner and partner.id == http.request.env.user.partner_id.id:
            return http.request.redirect('/home/my-courses')
        else:
            data = {
                'partner': partner
            }
            student_user = http.request.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            student_user_id = student_user.id

            enrollments = http.request.env['op.course.enrollment'].sudo().search(
                [('user_id', '=', student_user_id),
                ('state', 'in', ['in_progress', 'done'])])
            if enrollments:
                data.update(self.my_course_details(enrollments))
            return http.request.render('stem_frontend_theme.stem_profile_courses', data)

    def new_access_token(self):
        return uuid.uuid4().hex


    @http.route('/rating/post', type='http', auth="public", website=True)
    def rating(self, **kw):
        res_name = kw.get('res_name')
        res_model = kw.get('res_model')
        res_id  = kw.get('res_id')
        rating = kw.get('rating')
        feedback = kw.get('message')
        access_token = self.new_access_token()
        course_id = kw.get('course_id')
        


        rate = http.request.env['rating.rating'].sudo().create({
            'res_name': res_name,
            'res_model': res_model,
            'res_id': res_id,
            'rating': rating,
            'feedback': feedback,
            'access_token': access_token,
            'consumed': True,
            'website_published': True
            })

        if rate:
            message_id = tools.generate_tracking_message_id(''+ res_id + '-' + res_model + '')
            email_from = http.request.env.user.name + " " + http.request.env.user.login
            msg = http.request.env['mail.message'].sudo().create({
                'subject': 'Re: ' + res_name,
                'subtype_id': 1,
                'res_id': res_id,
                'message_id': message_id,
                'body': feedback,
                'record_name': res_name,
                'no_auto_thread': False,
                'reply_to': 'OpenEduCat <catchall@gmail.com>',
                'author_id': http.request.env.user.partner_id.id,
                'model': res_model,
                'message_type': 'comment',
                'email_from': email_from
                })
            rate.write({'message_id': msg.id})

        return http.request.redirect('/course-detail/' + course_id)

    @http.route(['/home/my-question',
                 '/home/my-question/page/<int:page>'
    ], type='http', auth="public", website=True)
    def my_questions(self, search='', page=1, ppg=False, **post):
        data = self.get_menu_data()
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = 5
            post["ppg"] = ppg
        else:
            ppg = 5

            
        forum = request.env['forum.forum'].search([('id', '=', 2)])       
        url = '/home/my-question'
        pager = request.website.pager(url=url, total=len(data['my_questions']), page=page,
                                      step=ppg, scope=7,
                                      url_args=post)
        
        my_question_ids = request.env['forum.post'].search([
                ('parent_id', '=', False),
                ('forum_id', '=', 2), ('create_uid', '=', http.request.env.user.id)],
                limit=ppg, offset=pager['offset'],order='relevancy desc')
        data['my_question_ids']= my_question_ids 
        data['forum']=forum
        data['pager']=pager
        return http.request.render('stem_frontend_theme.stem_my_question', data);

    @http.route('/home/session/change_password', type="http", method="POST", auth="user", website=True, csrf=False)
    def change_password(self, **kw):
        old_password = kw.get('old_password')
        new_password = kw.get('new_password')
        confirm_password = kw.get('confirm_password')
        result = {}
        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            result = {
                'error':'Bạn không thể để trống bất kỳ mật khẩu nào.'
            }
            return str(json.dumps(result))

        if new_password != confirm_password:
            result = {
                'error': 'Mật khẩu mới không khớp với mật khẩu xác nhận.'
            }
            return str(json.dumps(result))

        try:
            if http.request.env['res.users'].change_password(old_password, new_password):
                result = {
                    'success':'Thay đổi mật khẩu thành công.'
                }
                return str(json.dumps(result))

        except Exception:
            result = {
                'error':'Mật khẩu cũ mà bạn cung cấp không chính xác, mật khẩu của bạn không được thay đổi.'
            }
            return str(json.dumps(result))

        result = {
            'error': 'Error, Mật khẩu của bạn không được thay đổi !'
        }
        return str(json.dumps(result))


class Website(Website):
    @http.route(auth='public')
    def index(self, data={}, **kw):
        super(Website, self).index(**kw)

        if http.request.session.uid:                        
            stem = Stem()
            data = stem.get_menu_data()

            return http.request.render('stem_frontend_theme.stem_home', data)        
        else:

            try:   
                providers = http.request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
            except Exception:   
                providers = []  
            for provider in providers:   
                return_url = http.request.httprequest.url_root + 'auth_oauth/signin'

                redirect = http.request.params.get('redirect') or 'home'
                if not redirect.startswith(('//', 'http://', 'https://')):
                    redirect = '%s%s' % (http.request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
                state = dict(
                    d=http.request.session.db,
                    p=provider['id'],
                    r=werkzeug.url_quote_plus(redirect),
                )
                token = http.request.params.get('token')
                if token:
                    state['t'] = token

                params = dict(    
                    response_type='token',    
                    client_id=provider['client_id'],    
                    redirect_uri=return_url,    
                    scope=provider['scope'],    
                    state=json.dumps(state),   
                )   
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))

            online_free_courses = http.request.env['op.course'].sudo().search(
                [], limit=5, order='create_date desc')

            all_users = http.request.env['res.users'].sudo().search([])    
            count_all_users = len(all_users)
            all_courses = http.request.env['op.course'].sudo().search([])
            count_all_courses = len(all_courses)
            all_blog_posts = http.request.env['blog.post'].sudo().search([])
            count_all_blog_posts = len(all_blog_posts)


            data = { 
                'online_free_courses': online_free_courses,
                'providers': providers,
                'count_all_users': count_all_users,
                'count_all_courses': count_all_courses, 
                'count_all_blog_posts': count_all_blog_posts
            }

            return http.request.render('stem_frontend_theme.stem_homepage', data)


class AuthSignupHomeTwo(Home):    
    def do_signup(self, qcontext):                
        """ Shared helper that creates a res.partner out of a token """                
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }

        if qcontext.get('gender'):
            values['gender'] = qcontext.get('gender')

        if qcontext.get('bd_year') and qcontext.get('bd_month') and qcontext.get('bd_date'):
            values['birthday'] = qcontext.get('bd_year') + '-' + qcontext.get('bd_month') + '-' + qcontext.get('bd_date')       
        assert values.values(), "The form was not properly filled in. "                
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."                
        supported_langs = [lang['code'] for lang in http.request.env['res.lang'].sudo().search_read([], ['code'])]                
        if http.request.lang in supported_langs:                        
            values['lang'] = http.request.lang
        self._signup_with_values(qcontext.get('token'), values)                
        http.request.env.cr.commit()



class SignupVerifyEmail(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        if (http.request.params.get("login") and http.request.params.get("password")):
            return self.passwordless_signup(http.request.params)
        else:
            return super(SignupVerifyEmail, self).web_auth_signup(*args, **kw)

    def passwordless_signup(self, values):
        qcontext = self.get_auth_signup_qcontext()

        try:   
            providers = http.request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:   
            providers = []  
        for provider in providers:   
            return_url = http.request.httprequest.url_root + 'auth_oauth/signin'

            redirect = http.request.params.get('redirect') or ''
            if not redirect.startswith(('//', 'http://', 'https://')):
                redirect = '%s%s' % (http.request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
            state = dict(
                d=http.request.session.db,
                p=provider['id'],
                r=werkzeug.url_quote_plus(redirect),
            )
            token = http.request.params.get('token')
            if token:
                state['t'] = token

            params = dict(    
                response_type='token',    
                client_id=provider['client_id'],    
                redirect_uri=return_url,    
                scope=provider['scope'],    
                state=json.dumps(state),   
            )   
            provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))

        online_free_courses = http.request.env['op.course'].sudo().search(
            [], limit=5, order='create_date desc')

        all_users = http.request.env['res.users'].sudo().search([])    
        count_all_users = len(all_users)
        all_courses = http.request.env['op.course'].sudo().search([])
        count_all_courses = len(all_courses)
        all_blog_posts = http.request.env['blog.post'].sudo().search([])
        count_all_blog_posts = len(all_blog_posts)


        qcontext['online_free_courses'] =  online_free_courses
        qcontext['providers'] = providers
        qcontext['count_all_users'] = count_all_users
        qcontext['count_all_courses'] = count_all_courses 
        qcontext['count_all_blog_posts'] = count_all_blog_posts


        """ Shared helper that creates a res.partner out of a token """                
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        

        if qcontext.get('gender'):
            values['gender'] = qcontext.get('gender')

        if qcontext.get('bd_year') and qcontext.get('bd_month') and qcontext.get('bd_date'):
            values['birthday'] = qcontext.get('bd_year') + '-' + qcontext.get('bd_month') + '-' + qcontext.get('bd_date')       
        assert values.values(), "The form was not properly filled in. "                
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."                
        supported_langs = [lang['code'] for lang in http.request.env['res.lang'].sudo().search_read([], ['code'])]                
        if http.request.lang in supported_langs:                        
            values['lang'] = http.request.lang

        # Check good format of e-mail
        if not validate_email(values.get("login", "")):
            qcontext["error"] = _("That does not seem to be an email address.")
            return http.request.render("stem_frontend_theme.stem_homepage", qcontext)
        elif not values.get("email"):
            values["email"] = values.get("login")

        if http.request.env["res.users"].sudo().search([("login", "=", values.get("login"))]):
            qcontext["error"] = _("Một người dùng khác đã được đăng ký sử dụng địa chỉ email này.")
            return http.request.render("stem_frontend_theme.stem_homepage", qcontext)

        # Remove password
        values["password"] = ""

        
        sudo_users = (http.request.env["res.users"]
                      .with_context(create_user=True).sudo())

        try:
            with http.request.cr.savepoint():
                sudo_users.signup(values, qcontext.get("token"))
                sudo_users.reset_password(values.get("login"))
        except Exception as error:
            # Duplicate key or wrong SMTP settings, probably
            _logger.exception(error)
            # Agnostic message for security
            qcontext["error"] = _(
                "Đã xảy ra sự cố, vui lòng thử lại sau hoặc liên hệ với chúng tôi.")
            return http.request.render("stem_frontend_theme.stem_homepage", qcontext)

        qcontext["message"] = _("Kiểm tra email của bạn để kích hoạt tài khoản của bạn!")
        return http.request.render("auth_signup.reset_password", qcontext)
        
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
