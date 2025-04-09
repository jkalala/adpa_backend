from django.core.management.base import BaseCommand
from members.models import Member, Project, Document, Event
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with initial ADPA data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding ADPA data...')
        
        # Clear existing data
        Member.objects.all().delete()
        Project.objects.all().delete()
        Document.objects.all().delete()
        Event.objects.all().delete()

        # Create Members
        members_data = [
            {
                'country': 'Angola',
                'status': 'Active',
                'since': 2015,
                'tier': 'Full',
                'payment_status': 'Current',
                'representative': 'José Eduardo',
                'latitude': -12.35,
                'longitude': 17.51
            },
            # Add all other members...
        ]
        
        for data in members_data:
            Member.objects.create(**data)

        # Create Projects
        projects_data = [
            {
                'name': 'Regional Infrastructure Development',
                'description': 'Improving cross-border transportation networks',
                'countries': 'Angola,Namibia,South Africa',
                'status': 'Active',
                'budget': 2500000,
                'progress': 65,
                'start_date': datetime.now() - timedelta(days=180),
                'end_date': datetime.now() + timedelta(days=90),
                'implementing_agency': 'ADPA Regional Committee'
            },
            # Add other projects...
        ]
        
        for data in projects_data:
            Project.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded ADPA data'))