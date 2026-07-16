# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request

class AccaController(http.Controller):

    @http.route('/acca/register', type='http', auth='public', website=True, methods=['GET'])
    def acca_register_form(self, **kwargs):
        """Render the ACCA registration web form."""
        return request.render('acca_registration.acca_register_form_template', {})

    @http.route('/acca/register/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def acca_register_submit(self, **post):
        """Process the registration form submission matching the Zoho format."""
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        email = post.get('email')
        
        # Mandatory fields validation
        if not first_name or not last_name or not email:
            return request.render('acca_registration.acca_register_form_template', {
                'error': 'First Name, Last Name, and Email ID are required fields.',
                'values': post
            })

        # Process multiple checkboxes for Highest Qualification
        qualifications = request.httprequest.form.getlist('highest_qualification')
        if not qualifications:
            single_val = post.get('highest_qualification')
            qualifications = [single_val] if single_val else []
        highest_qualification_str = ", ".join(qualifications)

        # Handle Date of Birth (empty strings passed as False)
        dob = post.get('dob') or False

        # Profile Image upload (single file)
        image_file = request.httprequest.files.get('image_file')
        image_data = False
        image_filename = False
        if image_file:
            filename = image_file.filename
            if filename:
                image_filename = filename
                image_data = base64.b64encode(image_file.read())

        # Construct address details
        street = post.get('street', '')
        street2 = post.get('street2', '')
        city = post.get('city', '')
        state = post.get('state', '')
        zip_code = post.get('zip_code', '')
        country = post.get('country', '')
        
        addr_lines = [street]
        if street2:
            addr_lines.append(street2)
        addr_lines.append(f"{city}, {state} {zip_code}".strip(", "))
        if country:
            addr_lines.append(country)
        full_address = "\n".join(filter(None, addr_lines))

        # Initial fees checkbox
        initial_fees_paid = True if post.get('initial_fees_paid') == 'on' else False
        advance_payment = float(post.get('advance_payment', 0))

        # Prepare values for Odoo create method
        vals = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': post.get('phone'),
            'dob': dob,
            'email': email,
            'street': street,
            'street2': street2,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': country,
            'address': full_address,
            'highest_qualification': highest_qualification_str,
            'initial_fees_paid': initial_fees_paid,
            'advance_payment': advance_payment,
        }

        # Include profile picture if uploaded
        if image_data:
            vals.update({
                'image_file': image_data,
                'image_filename': image_filename,
            })

        # Create the ACCA Registration record in the database using sudo()
        registration_record = request.env['acca.registration'].sudo().create(vals)

        # Helper to create associated attachments for multiple files
        def create_attachments(files_list, prefix):
            Attachment = request.env['ir.attachment'].sudo()
            for f in files_list:
                if f and f.filename:
                    content = f.read()
                    if content:
                        Attachment.create({
                            'name': f"{prefix} {f.filename}",
                            'res_model': 'acca.registration',
                            'res_id': registration_record.id,
                            'datas': base64.b64encode(content),
                        })

        # Process multiple uploads
        id_proof_files = request.httprequest.files.getlist('id_proof_files')
        entry_req_files = request.httprequest.files.getlist('entry_req_files')
        exemption_req_files = request.httprequest.files.getlist('exemption_req_files')
        other_doc_files = request.httprequest.files.getlist('other_doc_files')

        create_attachments(id_proof_files, "[ID Proof]")
        create_attachments(entry_req_files, "[Entry Requirement]")
        create_attachments(exemption_req_files, "[Exemption Requirement]")
        create_attachments(other_doc_files, "[Other Document]")

        # Render success template
        return request.render('acca_registration.acca_register_success_template', {
            'registration': registration_record
        })
