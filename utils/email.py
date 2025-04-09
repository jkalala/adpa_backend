import uuid
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import EmailLog

def send_templated_email(
    template_name,
    context,
    subject,
    recipient_list,
    from_email=None,
    track=True
):
    """
    Send an HTML email using a template with optional tracking.
    """
    try:
        # Add tracking pixel and email ID if tracking is enabled
        email_id = uuid.uuid4() if track else None
        if track:
            tracking_pixel = f'<img src="{settings.SITE_URL}/email/track/{email_id}.png" />'
            context['tracking_pixel'] = tracking_pixel
            context['email_id'] = email_id

        # Add timestamp to context
        context['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Render email templates
        html_content = render_to_string(f'email/{template_name}.html', context)
        text_content = strip_tags(html_content)

        # Create email message
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list
        )
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send()

        # Log email if tracking is enabled
        if track:
            for recipient in recipient_list:
                EmailLog.objects.create(
                    email_id=email_id,
                    recipient=recipient,
                    subject=subject,
                    template_name=template_name,
                    status='sent'
                )

        return True, email_id

    except Exception as e:
        if track:
            EmailLog.objects.create(
                email_id=email_id,
                recipient=recipient_list[0],
                subject=subject,
                template_name=template_name,
                status='failed',
                error_message=str(e)
            )
        return False, str(e)

def send_welcome_email(user):
    """Send welcome email to new users."""
    context = {
        'user': user,
        'portal_link': f"{settings.SITE_URL}/dashboard/"
    }
    return send_templated_email(
        'welcome',
        context,
        'Welcome to ADPA!',
        [user.email]
    )

def send_password_reset_email(user, reset_token):
    """Send password reset email."""
    context = {
        'user': user,
        'reset_url': f"{settings.SITE_URL}/reset-password/{reset_token}/",
        'expiry_hours': 24
    }
    return send_templated_email(
        'password_reset',
        context,
        'Reset Your ADPA Password',
        [user.email]
    )

def send_event_registration_email(user, event, calendar_links):
    """Send event registration confirmation."""
    context = {
        'user': user,
        'event': event,
        'event_details_url': f"{settings.SITE_URL}/events/{event.id}/",
        'calendar_links': calendar_links
    }
    return send_templated_email(
        'event_registration',
        context,
        f'Registration Confirmed: {event.title}',
        [user.email]
    ) 