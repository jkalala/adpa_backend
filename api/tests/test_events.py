from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from adpa_events.models import Event, EventRegistration
from api.serializers import EventDetailSerializer
from datetime import datetime, timedelta

User = get_user_model()

class EventTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date=datetime.now() + timedelta(days=7),
            location='Test Location',
            is_public=True
        )
        self.url = reverse('event-list')

    def test_list_events(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_event_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'New Event',
            'description': 'New Description',
            'date': datetime.now() + timedelta(days=14),
            'location': 'New Location',
            'is_public': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_for_event(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('event-register', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            EventRegistration.objects.filter(
                user=self.user,
                event=self.event
            ).exists()
        )

    def test_duplicate_registration(self):
        self.client.force_authenticate(user=self.user)
        EventRegistration.objects.create(user=self.user, event=self.event)
        url = reverse('event-register', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 