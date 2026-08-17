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

    @http.route(['/kyc/admission', '/kyc/form', '/kyc'], type='http', auth='public', website=True, sitemap=True)
    def kyc_form_index(self, **kw):
        return request.render('kyc_forms.kyc_admission_form_template', {
            'subjects': ACCA_SUBJECTS,
            'values': kw,
        })

    @http.route('/kyc/admission/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def kyc_form_submit(self, **kw):
        # 1. Validate required text fields
        required_fields = [
            'first_name', 'last_name', 'phone', 'email', 'dob',
            'highest_qualification', 'street', 'city', 'state', 'zip_code', 'country',
            'acca_reg_number', 'referral_source'
        ]
        for field in required_fields:
            if not kw.get(field) or not str(kw.get(field)).strip():
                return request.render('kyc_forms.kyc_admission_form_template', {
                    'error': f'Please fill in the required field: {field.replace("_", " ").title()}',
                    'subjects': ACCA_SUBJECTS,
                    'values': kw,
                })

        # 2. Process image upload & enforce 1MB size limit
        image_file = request.httprequest.files.get('image_file')
        image_data = None
        image_filename = None

        if image_file and image_file.filename:
            file_content = image_file.read()
            # 1 MB = 1024 * 1024 bytes = 1,048,576 bytes
            if len(file_content) > 1048576:
                return request.render('kyc_forms.kyc_admission_form_template', {
                    'error': 'Image file size exceeds the maximum limit of 1 MB. Please upload a smaller photo.',
                    'subjects': ACCA_SUBJECTS,
                    'values': kw,
                })
            image_data = base64.b64encode(file_content)
            image_filename = image_file.filename

        # 3. Process languages
        languages_list = request.httprequest.form.getlist('languages')
        if not languages_list:
            return request.render('kyc_forms.kyc_admission_form_template', {
                'error': 'Please select at least one Language.',
                'subjects': ACCA_SUBJECTS,
                'values': kw,
            })
        languages_str = ", ".join(languages_list)

        # 4. Prepare KYC form values
        kyc_values = {
            'first_name': kw.get('first_name').strip(),
            'last_name': kw.get('last_name').strip(),
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

        # 5. Create KYC form record
        KycModel = request.env['kyc.form'].sudo()
        kyc_record = KycModel.create(kyc_values)

        # 6. Process pursuing subjects matrix
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

        _logger.info(f"Successfully created KYC Form record: {kyc_record.id} for {kyc_record.name}")

        return request.render('kyc_forms.kyc_admission_success_template', {
            'kyc': kyc_record,
        })
