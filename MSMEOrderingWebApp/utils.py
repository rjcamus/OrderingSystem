def get_or_create_customization():
    # Your logic here, e.g.:
    from .models import CustomizationSettings
    obj, _ = CustomizationSettings.objects.get_or_create(id=1)
    return obj

from datetime import datetime, timedelta
from django.utils import timezone
from .models import BusinessDetails

def get_business_day_range():
    business = BusinessDetails.objects.first()
    if not business or not business.opening_time or not business.closing_time:
        # fallback to calendar day
        today = timezone.localtime()
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end

    now = timezone.localtime()
    today = now.date()

    opening_time = business.opening_time
    closing_time = business.closing_time

    start = timezone.make_aware(datetime.combine(today, opening_time))
    end = timezone.make_aware(datetime.combine(today, closing_time))

    # Handle overnight case (e.g. 18:00 → 03:00 next day)
    if end <= start:
        end += timedelta(days=1)

    # If current time is after midnight but before closing, shift window back one day
    if now < start and now.time() < closing_time:
        start -= timedelta(days=1)
        end -= timedelta(days=1)

    return start, end

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_verification_email(to_email, verify_url):
    subject = "Verify Your Updated Email Address"
    text_content = f"Please verify your email by visiting: {verify_url}"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
            <div style="background-color: #f4f4f4; padding: 40px 0;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); padding: 40px 20px; border: 1px solid #e0e0e0;">
                    <div style="text-align: center;">
                        <h2 style="color: #4CAF50; font-size: 32px; font-weight: bold;">Email Verification</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.5; margin-top: 10px;">
                            You have updated your email. Please verify it to activate your account:
                        </p>
                    </div>
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{verify_url}" style="padding: 15px 30px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;">
                            VERIFY EMAIL
                        </a>
                    </div>
                    <p style="text-align: center; font-size: 14px; color: #888888; margin-top: 20px;">
                        If you did not request this change, please ignore this email.
                    </p>
                    <footer style="margin-top: 40px; text-align: center; font-size: 14px; color: #888888; padding: 10px 0; border-top: 2px solid #e0e0e0;">
                        <p style="color: #333333;">Online Ordering System</p>
                    </footer>
                </div>
            </div>
        </body>
    </html>
    """

    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
