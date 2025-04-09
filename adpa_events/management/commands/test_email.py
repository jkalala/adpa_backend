from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def handle(self, *args, **options):
        try:
            send_mail(
                'Test Email from ADPA',
                'This is a test email from your Django application.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully sent test email')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            ) 