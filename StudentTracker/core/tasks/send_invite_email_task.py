from celery import shared_task
from django.core.mail import send_mail
import requests
import os


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_invite_email(self, user_data, redirect_url):
    try:
        res = requests.post(
            f"{os.environ['SUPABASE_URL']}/auth/v1/invite",
            params={"redirect_to": redirect_url},
            headers={
                "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
                "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
            },
            json=user_data,
            timeout=10,
        )
        res.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc)