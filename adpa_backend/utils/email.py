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