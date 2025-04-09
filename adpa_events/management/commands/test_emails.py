from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Test various email functionalities'

    def handle(self, *args, **options):
        self.stdout.write('Testing email configuration...')

        # Verify template directory exists
        template_dir = os.path.join(settings.BASE_DIR, 'templates', 'email')
        if not os.path.exists(template_dir):
            self.stdout.write(
                self.style.WARNING(f'Creating template directory: {template_dir}')
            )
            os.makedirs(template_dir, exist_ok=True)

        # Verify welcome template exists
        welcome_template = os.path.join(template_dir, 'welcome.html')
        if not os.path.exists(welcome_template):
            self.stdout.write(
                self.style.WARNING(f'Welcome template not found at: {welcome_template}')
            )
            return

        # Test emails
        self.test_simple_email()
        self.test_html_email()
        self.test_template_email()

    def test_simple_email(self):
        try:
            send_mail(
                'Test Plain Text Email from ADPA',
                'This is a test email from your Django application.',
                settings.DEFAULT_FROM_EMAIL or 'test@example.com',
                ['test@example.com'],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Successfully sent plain text email')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send plain text email: {str(e)}')
            )

    def test_html_email(self):
        try:
            html_content = """
            <html>
                <body>
                    <h1>Test HTML Email</h1>
                    <p>This is a test HTML email from your Django application.</p>
                </body>
            </html>
            """
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(
                'Test HTML Email from ADPA',
                text_content,
                settings.DEFAULT_FROM_EMAIL or 'test@example.com',
                ['test@example.com']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            self.stdout.write(
                self.style.SUCCESS('✓ Successfully sent HTML email')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send HTML email: {str(e)}')
            )

    def test_template_email(self):
        try:
            context = {
                'user': {
                    'first_name': 'Test',
                    'email': 'test@example.com'
                }
            }
            
            html_content = render_to_string('email/welcome.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                'Test Template Email from ADPA',
                text_content,
                settings.DEFAULT_FROM_EMAIL or 'test@example.com',
                ['test@example.com']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            self.stdout.write(
                self.style.SUCCESS('✓ Successfully sent template email')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send template email: {str(e)}')
            ) 