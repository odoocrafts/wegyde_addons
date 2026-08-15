# -*- coding: utf-8 -*-
import base64
import requests
import json
import hmac
import hashlib
import logging
from odoo import http
from odoo.http import request

class AccaController(http.Controller):

    @http.route('/acca/register', type='http', auth='public', methods=['GET'])
    def acca_register_form(self, **kwargs):
        """Render the ACCA registration web form."""
        default_fee = request.env['ir.config_parameter'].sudo().get_param('acca_registration.default_fee', default=0.0)
        try:
            default_fee = float(default_fee)
        except (ValueError, TypeError):
            default_fee = 0.0
        return request.render('acca_registration.acca_register_form_template', {
            'default_fee': default_fee,
        })

    @http.route('/acca/register/submit', type='http', auth='public', methods=['POST'], csrf=True)
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

        # Payment Choice & Fee Calculation
        payment_choice = post.get('payment_choice', 'online')
        
        is_bcom_pursuing = any(
            q in qualifications for q in [
                'B.Com Pursuing - Conditional Exemption',
                'B.Com Pursuing - Conditional Exemption(Standard)'
            ]
        )
        
        default_fee = request.env['ir.config_parameter'].sudo().get_param('acca_registration.default_fee', default=0.0)
        try:
            default_fee = float(default_fee)
        except (ValueError, TypeError):
            default_fee = 0.0

        if is_bcom_pursuing:
            fee_to_charge = 21499.0
        elif default_fee > 0:
            fee_to_charge = default_fee
        else:
            try:
                advance_payment_val = float(post.get('advance_payment', 4500))
                fee_to_charge = advance_payment_val if advance_payment_val > 0 else 4500.0
            except (ValueError, TypeError):
                fee_to_charge = 4500.0

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
            'initial_fees_paid': False,
            'payment_status': 'pending',
            'advance_payment': fee_to_charge,
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

        # If User Chose to Pay Later at Office
        if payment_choice == 'pay_later':
            return request.render('acca_registration.acca_register_success_template', {
                'registration': registration_record,
                'payment_choice': 'pay_later',
                'fee_amount': fee_to_charge,
            })

        # --- Razorpay Integration for Online Payment ---
        razorpay_key_id = request.env['ir.config_parameter'].sudo().get_param('acca_registration.razorpay_key_id', default='')
        razorpay_key_secret = request.env['ir.config_parameter'].sudo().get_param('acca_registration.razorpay_key_secret', default='')
        
        if razorpay_key_id and razorpay_key_secret and fee_to_charge > 0:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
            payload = {
                "amount": int(fee_to_charge * 100),
                "currency": "INR",
                "accept_partial": False,
                "reference_id": str(registration_record.id),
                "description": "ACCA Registration Fee",
                "customer": {
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "contact": post.get('phone', '')
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "callback_url": f"{base_url}/acca/payment/success?ref={registration_record.id}",
                "callback_method": "get"
            }
            
            try:
                response = requests.post(
                    "https://api.razorpay.com/v1/payment_links",
                    json=payload,
                    auth=(razorpay_key_id, razorpay_key_secret),
                    timeout=10
                )
                if response.status_code == 200:
                    resp_data = response.json()
                    payment_link_id = resp_data.get('id')
                    short_url = resp_data.get('short_url')
                    
                    if payment_link_id and short_url:
                        registration_record.sudo().write({
                            'razorpay_payment_link_id': payment_link_id,
                        })
                        return request.redirect(short_url, local=False)
                else:
                    logging.getLogger(__name__).error(f"Razorpay Payment Link generation failed: {response.text}")
            except Exception as e:
                logging.getLogger(__name__).error(f"Error generating Razorpay Payment Link: {str(e)}")

        # Fallback if no payment link generated or Razorpay not configured
        return request.render('acca_registration.acca_register_success_template', {
            'registration': registration_record,
            'payment_choice': 'online_fallback',
            'fee_amount': fee_to_charge,
        })

    @http.route('/acca/payment/success', type='http', auth='public', methods=['GET'])
    def acca_payment_success(self, **kwargs):
        ref = kwargs.get('ref')
        razorpay_payment_id = kwargs.get('razorpay_payment_id')
        razorpay_payment_link_id = kwargs.get('razorpay_payment_link_id')
        
        registration = False
        if ref:
            registration = request.env['acca.registration'].sudo().browse(int(ref))
            if not registration.exists():
                registration = False
                
        return request.render('acca_registration.acca_payment_success_template', {
            'registration': registration,
            'payment_id': razorpay_payment_id,
            'payment_link_id': razorpay_payment_link_id
        })

    @http.route('/acca/razorpay/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def acca_razorpay_webhook(self, **kwargs):
        payload = request.httprequest.data
        webhook_signature = request.httprequest.headers.get('X-Razorpay-Signature')
        webhook_secret = request.env['ir.config_parameter'].sudo().get_param('acca_registration.razorpay_webhook_secret', default='')
        
        if not webhook_secret or not webhook_signature:
            return request.make_response("Unauthorized", status=401)
            
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, webhook_signature):
            return request.make_response("Invalid Signature", status=400)
            
        try:
            data = json.loads(payload.decode('utf-8'))
        except ValueError:
            return request.make_response("Invalid JSON", status=400)
            
        event = data.get('event')
        if event == 'payment_link.paid':
            payment_link_entity = data.get('payload', {}).get('payment_link', {}).get('entity', {})
            reference_id = payment_link_entity.get('reference_id')
            
            if reference_id:
                try:
                    registration = request.env['acca.registration'].sudo().browse(int(reference_id))
                    if registration.exists():
                        registration.sudo().write({
                            'payment_status': 'paid',
                            'initial_fees_paid': True,
                        })
                        return request.make_response("OK", status=200)
                except ValueError:
                    pass
                    
        return request.make_response("Ignored", status=200)
