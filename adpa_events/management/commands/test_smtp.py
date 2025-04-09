from django.core.management.base import BaseCommand
import socket
import smtplib
from email.mime.text import MIMEText
from django.conf import settings

class Command(BaseCommand):
    help = 'Test SMTP connection and DNS resolution'

    def handle(self, *args, **options):
        # Test DNS resolution
        self.stdout.write('Testing DNS resolution...')
        try:
            ip = socket.gethostbyname('smtp.gmail.com')
            self.stdout.write(self.style.SUCCESS(f'Successfully resolved smtp.gmail.com to {ip}'))
        except socket.gaierror as e:
            self.stdout.write(self.style.ERROR(f'DNS resolution failed: {str(e)}'))
            return

        # Test SMTP connection
        self.stdout.write('Testing SMTP connection...')
        try:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.ehlo()
                server.starttls()
                self.stdout.write(self.style.SUCCESS('Successfully connected to SMTP server'))
                
                # Try to login if credentials are provided
                if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                    try:
                        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        self.stdout.write(self.style.SUCCESS('Successfully logged in to SMTP server'))
                    except smtplib.SMTPAuthenticationError as e:
                        self.stdout.write(self.style.ERROR(f'Authentication failed: {str(e)}'))
                        return
                
                # Try to send a test email
                try:
                    msg = MIMEText('Test email content')
                    msg['Subject'] = 'Test email'
                    msg['From'] = settings.DEFAULT_FROM_EMAIL
                    msg['To'] = settings.DEFAULT_FROM_EMAIL
                    
                    server.send_message(msg)
                    self.stdout.write(self.style.SUCCESS('Successfully sent test email'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'SMTP connection failed: {str(e)}')) 