from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from adpa_events.models import Event, EventRegistration
from members.models import Member, Project, Document
import random
from datetime import timedelta
import os
from django.core.files.base import ContentFile

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def create_test_file(self, filename, content=b"Test file content"):
        return ContentFile(content, name=filename)

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create superuser
        if not User.objects.filter(email='admin@adpa.org').exists():
            admin = User.objects.create_superuser(
                email='admin@adpa.org',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin.email}'))

        # Create regular users
        test_users = []
        for i in range(5):
            email = f'user{i+1}@example.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='testpass123',
                    first_name=f'User{i+1}',
                    last_name='Test'
                )
                test_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))

        # Create members
        countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Japan']
        statuses = ['Active', 'Observer', 'Inactive']
        
        for i in range(10):
            member, created = Member.objects.get_or_create(
                name=f'Member Organization {i+1}',
                defaults={
                    'country': random.choice(countries),
                    'status': random.choice(statuses),
                    'join_date': timezone.now() - timedelta(days=random.randint(1, 365)),
                    'description': f'Description for member organization {i+1}',
                    'website': f'https://member{i+1}.example.com'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created member: {member.name}'))

        # Create projects
        project_types = ['Research', 'Development', 'Education', 'Outreach']
        for i in range(8):
            project, created = Project.objects.get_or_create(
                title=f'Project {i+1}',
                defaults={
                    'description': f'Description for project {i+1}',
                    'type': random.choice(project_types),
                    'start_date': timezone.now() - timedelta(days=random.randint(1, 180)),
                    'end_date': timezone.now() + timedelta(days=random.randint(1, 180)),
                    'status': random.choice(['Active', 'Completed', 'On Hold']),
                    'progress': random.randint(0, 100)
                }
            )
            if created:
                project.countries = random.sample(countries, random.randint(1, 3))
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))

        # Create documents
        categories = ['Report', 'Policy', 'Research', 'Minutes', 'General']
        for i in range(6):
            doc, created = Document.objects.get_or_create(
                title=f'Document {i+1}',
                defaults={
                    'description': f'Description for document {i+1}',
                    'category': random.choice(categories),
                    'file': self.create_test_file(f'document_{i+1}.pdf'),
                    'upload_date': timezone.now() - timedelta(days=random.randint(1, 90)),
                    'download_count': random.randint(0, 100)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created document: {doc.title}'))

        # Create events
        event_types = ['Conference', 'Workshop', 'Webinar', 'Meeting']
        locations = ['New York', 'London', 'Tokyo', 'Paris', 'Sydney', 'Berlin', 'Toronto']
        
        for i in range(12):
            future = random.choice([True, False])
            event_date = timezone.now() + timedelta(days=random.randint(1, 180)) if future \
                        else timezone.now() - timedelta(days=random.randint(1, 180))
            
            event, created = Event.objects.get_or_create(
                title=f'Event {i+1}',
                defaults={
                    'description': f'Description for event {i+1}',
                    'date': event_date,
                    'location': random.choice(locations),
                    'type': random.choice(event_types),
                    'capacity': random.randint(20, 200),
                    'is_public': random.choice([True, False])
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created event: {event.title}'))

                # Create random registrations for future events
                if future:
                    for user in random.sample(test_users, random.randint(0, len(test_users))):
                        registration, reg_created = EventRegistration.objects.get_or_create(
                            event=event,
                            user=user,
                            defaults={
                                'registration_date': timezone.now(),
                                'attended': False
                            }
                        )
                        if reg_created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created registration: {user.email} for {event.title}'
                                )
                            )

        self.stdout.write(self.style.SUCCESS('Successfully populated test data')) 