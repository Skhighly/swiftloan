import requests
import base64
from datetime import datetime
from django.conf import settings


def get_mpesa_token():
    """Get OAuth access token from Daraja API."""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    if not consumer_key or not consumer_secret:
        return None

    env = settings.MPESA_ENVIRONMENT
    if env == 'production':
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret), timeout=30)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"M-Pesa token error: {e}")
        return None


def initiate_stk_push(phone_number, amount, account_reference, description, callback_url=None):
    """
    Initiate M-Pesa STK Push (Lipa Na M-Pesa Online).
    Returns dict with success status and response data.
    """
    token = get_mpesa_token()
    if not token:
        return {
            'success': False,
            'error': 'Could not authenticate with M-Pesa. Please check your API credentials.',
            'mock': True,
        }

    env = settings.MPESA_ENVIRONMENT
    if env == 'production':
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    else:
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()
    cb_url = callback_url or settings.MPESA_CALLBACK_URL

    # Normalize phone number to 2547XXXXXXXX
    phone = str(phone_number).strip()
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('07'):
        phone = '254' + phone[1:]

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": cb_url,
        "AccountReference": account_reference,
        "TransactionDesc": description,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        if data.get('ResponseCode') == '0':
            return {
                'success': True,
                'checkout_request_id': data.get('CheckoutRequestID'),
                'merchant_request_id': data.get('MerchantRequestID'),
                'response_description': data.get('ResponseDescription'),
            }
        else:
            return {
                'success': False,
                'error': data.get('errorMessage', 'STK push failed'),
                'data': data,
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}
