from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
import uuid
import os

class Command(BaseCommand):
    help = 'Verify email template rendering and sending'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
            default='test@example.com'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting email verification...')

        # 1. Check template directory
        template_dir = os.path.join(settings.BASE_DIR, 'templates', 'email')
        self.check_directory(template_dir)

        # 2. Check template file
        template_file = os.path.join(template_dir, 'test.html')
        self.check_template(template_file)

        # 3. Test template rendering
        self.test_template_rendering()

        # 4. Send test email
        self.send_test_email(options['email'])

    def check_directory(self, directory):
        if not os.path.exists(directory):
            self.stdout.write(self.style.WARNING(f'Creating directory: {directory}'))
            os.makedirs(directory, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'✓ Template directory exists: {directory}'))

    def check_template(self, template_file):
        if not os.path.exists(template_file):
            self.stdout.write(self.style.ERROR(f'✗ Template file not found: {template_file}'))
            return False
        self.stdout.write(self.style.SUCCESS(f'✓ Template file exists: {template_file}'))
        return True

    def test_template_rendering(self):
        try:
            context = {
                'name': 'Test User',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'test_link': 'https://example.com/test',
                'email_id': str(uuid.uuid4())
            }
            
            html_content = render_to_string('email/test.html', context)
            text_content = strip_tags(html_content)
            
            self.stdout.write(self.style.SUCCESS('✓ Template rendered successfully'))
            self.stdout.write('\nText version preview:')
            self.stdout.write('-' * 40)
            self.stdout.write(text_content[:200] + '...')
            self.stdout.write('-' * 40)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Template rendering failed: {str(e)}'))
            return False
        return True

    def send_test_email(self, recipient_email):
        try:
            # Prepare email content
            context = {
                'name': 'Test User',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'test_link': 'https://example.com/test',
                'email_id': str(uuid.uuid4())
            }
            
            html_content = render_to_string('email/test.html', context)
            text_content = strip_tags(html_content)
            
            # Create email message
            subject = 'ADPA Email System Test'
            from_email = settings.DEFAULT_FROM_EMAIL or 'test@example.com'
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Test email sent to {recipient_email}'))
            self.stdout.write('\nEmail details:')
            self.stdout.write(f'From: {from_email}')
            self.stdout.write(f'To: {recipient_email}')
            self.stdout.write(f'Subject: {subject}')
            self.stdout.write(f'Email ID: {context["email_id"]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send email: {str(e)}'))
            return False
        return True 