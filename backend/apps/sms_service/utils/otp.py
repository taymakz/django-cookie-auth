from django.conf import settings
import json

import requests


def sms_service_send_otp(phone: str, otp: str) -> bool:
    url = getattr(settings, "SMS_SERVICE_API_URL", None)
    secret_key = getattr(settings, "SMS_SERVICE_SECRET_KEY", None)
    pattern = getattr(settings, "SMS_SERVICE_OTP_PATTERN", None)
    site_url = getattr(settings, "SITE_URL", None)
    if not url or not secret_key or not pattern:
        raise ValueError("SMS service configuration is incomplete.")
    data = json.dumps(
        {
            "phone": phone,
            "code": otp,
            "pattern": pattern,
            "callback_url": f"{site_url}/api/admin/sms-service/result/otp/",
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": secret_key}

    try:
        response = requests.post(f"{url}/api/", data=data, headers=headers)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error sending OTP: {e}")
        return False
