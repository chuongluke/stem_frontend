{
    "name": "STEM Frontend Theme",
    "summary": "STEM Frontend Theme",
    "category": "Themes/Frontend",
    "author": "BU1 - DTT",
    "website": "http://dtt.vn",
    "description": """
        STEM Frontend Theme
    """,
    "author": "BU1 - DTT",
    "external_dependencies": {
        "python": [
            "lxml",
            "validate_email",
        ],
    },
    "depends": [
        'base',
        'website',
        'openeducat_lms',
        'auth_oauth',
        'web',
        'openeducat_core',
        'mail',
        'contacts',
        'stem_tables',
        'website_forum',
        'website_mail',
        'rating'
    ],
    "data": [
        'views/assets.xml',
        'views/web.xml',
        'views/home.xml',
        'views/course_detail.xml',
        'views/homepage.xml',
        'views/my_courses.xml',
        'views/my_blogs.xml',
        'views/my_mes.xml',
        'views/register_parent_mail_template.xml',
        'views/alert.xml',
        'views/my_mes_detail.xml',
        'views/my_child_courses.xml',
        'views/view_faculty.xml',
        'views/signup.xml',
        'views/faculty_mail_template.xml',
        'views/material_detail_view.xml',
        'views/search_results.xml',
        'views/my_courses_teach.xml',
        'views/web_forum.xml',
        'views/profile.xml',
        'views/profile_blogs.xml',
        'views/profile_courses.xml',
        'views/my_question.xml',
        'views/all_courses.xml'
    ],
}

