# -*- coding: utf-8 -*-
import base64
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

ACCA_SUBJECTS = [
    ('BT', 'Business Technology (BT)'),
    ('MA', 'Management Accounting (MA)'),
    ('FA', 'Financial Accounting (FA)'),
    ('LW', 'Law (LW)'),
    ('PM', 'Performance Management (PM)'),
    ('FR', 'Financial Reporting (FR)'),
    ('AA', 'Audit & Assurance (AA)'),
    ('TX', 'Taxation (TX)'),
    ('FM', 'Financial Management (FM)'),
    ('SBR', 'Strategic Business Reporting (SBR)'),
    ('SBL', 'Strategic Business Leader (SBL)'),
    ('APM', 'Advanced Performance Management (APM)'),
    ('AFM', 'Advanced Financial Management (AFM)'),
    ('ATX', 'Advanced Taxation (ATX)'),
    ('AAA', 'Advanced Audit & Assurance (AAA)'),
]

class KycFormController(http.Controller):

    # 1. RENDER KYC FORM USING STUDENT ID IN URL PATH
    @http.route([
        '/kyc/admission/<int:student_id>',
        '/kyc/form/<int:student_id>',
        '/kyc/<int:student_id>',
        '/kyc/admission',
    ], type='http', auth='public', website=True, sitemap=False)
    def kyc_form_index(self, student_id=None, **kw):
        # Read student_id from URL path or query parameter
        s_id = student_id or kw.get('student_id')
        if not s_id:
            return request.render('website.404', {})

        student = request.env['student.student'].sudo().browse(int(s_id))
        if not student.exists():
            return request.render('website.404', {})

        return request.render('kyc_forms.kyc_admission_form_template', {
            'student': student,
            'subjects': ACCA_SUBJECTS,
            'values': kw,
        })

    # 2. SUBMIT KYC FORM
    @http.route('/kyc/admission/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def kyc_form_submit(self, **kw):
        student_id = kw.get('student_id')
        if not student_id:
            return request.render('website.404', {})

        student = request.env['student.student'].sudo().browse(int(student_id))
        if not student.exists():
            return request.render('website.404', {})

        # Validation
        required_fields = [
            'phone', 'email', 'dob', 'highest_qualification',
            'street', 'city', 'state', 'zip_code', 'country',
            'acca_reg_number', 'referral_source'
        ]
        for field in required_fields:
            if not kw.get(field) or not str(kw.get(field)).strip():
                return request.render('kyc_forms.kyc_admission_form_template', {
                    'error': f'Please fill in the required field: {field.replace("_", " ").title()}',
                    'student': student,
                    'subjects': ACCA_SUBJECTS,
                    'values': kw,
                })

        # Image Upload (Max 1MB)
        image_file = request.httprequest.files.get('image_file')
        image_data = None
        image_filename = None
        if image_file and image_file.filename:
            file_content = image_file.read()
            if len(file_content) > 1048576:
                return request.render('kyc_forms.kyc_admission_form_template', {
                    'error': 'Image file size exceeds the maximum limit of 1 MB. Please upload a smaller photo.',
                    'student': student,
                    'subjects': ACCA_SUBJECTS,
                    'values': kw,
                })
            image_data = base64.b64encode(file_content)
            image_filename = image_file.filename

        # Languages
        languages_list = request.httprequest.form.getlist('languages')
        if not languages_list:
            return request.render('kyc_forms.kyc_admission_form_template', {
                'error': 'Please select at least one Language.',
                'student': student,
                'subjects': ACCA_SUBJECTS,
                'values': kw,
            })
        languages_str = ", ".join(languages_list)

        # Prepare Values
        kyc_values = {
            'student_id': student.id,
            'phone': kw.get('phone').strip(),
            'email': kw.get('email').strip(),
            'dob': kw.get('dob'),
            'image_file': image_data,
            'image_filename': image_filename,
            'highest_qualification': kw.get('highest_qualification'),
            'street': kw.get('street').strip(),
            'street2': kw.get('street2', '').strip() if kw.get('street2') else '',
            'city': kw.get('city').strip(),
            'state': kw.get('state').strip(),
            'zip_code': kw.get('zip_code').strip(),
            'country': kw.get('country'),
            'acca_reg_number': kw.get('acca_reg_number').strip(),
            'languages': languages_str,
            'referral_source': kw.get('referral_source'),
        }

        # Create KYC record
        kyc_record = request.env['kyc.form'].sudo().create(kyc_values)

        # Process subjects
        SubjectModel = request.env['kyc.pursuing.subject'].sudo()
        for code, name in ACCA_SUBJECTS:
            pkg = kw.get(f'pkg_{code}')
            if pkg and pkg in ['Basic', 'Standard', 'Premium', 'Offline']:
                SubjectModel.create({
                    'kyc_form_id': kyc_record.id,
                    'subject_code': code,
                    'subject_name': name,
                    'package_type': pkg,
                })

        # Update student status
        if hasattr(student, 'kyc_status'):
            student.sudo().write({'kyc_status': 'submitted'})

        return request.render('kyc_forms.kyc_admission_success_template', {
            'kyc': kyc_record,
            'student': student,
        })