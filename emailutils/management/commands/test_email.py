from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from emailutils.utils import send_templated_email
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the email system'

    def handle(self, *args, **options):
        self.stdout.write('Starting email system test...')
        
        # Test email address
        test_email = 'joaquim.kalala@email.com'  # Hardcoded for testing
        
        # Check template directory
        template_dir = os.path.join(settings.BASE_DIR, 'templates', 'email')
        if not os.path.exists(template_dir):
            self.stdout.write(self.style.ERROR(f'Template directory not found: {template_dir}'))
            return
        self.stdout.write(self.style.SUCCESS('✓ Template directory exists'))

        # Check test template
        template_path = os.path.join(template_dir, 'test.html')
        if not os.path.exists(template_path):
            self.stdout.write(self.style.ERROR(f'Test template not found: {template_path}'))
            return
        self.stdout.write(self.style.SUCCESS('✓ Test template exists'))

        # Send test email
        self.stdout.write(f'Sending test email to {test_email}...')
        
        context = {
            'name': 'Test User',
            'email': test_email,
            'timestamp': 'test timestamp'
        }
        
        success, result = send_templated_email(
            template_name='test',
            context=context,
            subject='ADPA Email System Test',
            recipient_list=[test_email]
        )

        if success:
            self.stdout.write(self.style.SUCCESS(f'✓ Test email sent successfully (ID: {result})'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send test email: {result}'))

        # Print email backend info
        self.stdout.write('\nEmail configuration:')
        self.stdout.write(f'Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'Use TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'From Email: {settings.DEFAULT_FROM_EMAIL}')