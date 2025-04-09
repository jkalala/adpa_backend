from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event, EventRegistration
from adpa_events.models import Survey  # Import Survey from adpa_events
from django.contrib.auth import get_user_model

User = get_user_model()

class EventAPITests(APITestCase):
    """Tests for event-related endpoints"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date='2024-01-01T00:00:00Z',
            end_date='2024-01-02T00:00:00Z',
            location='Test Location',
            organizer=self.user
        )
        
        # Create test survey
        self.survey = Survey.objects.create(
            title='Test Survey',
            description='Test Survey Description',
            event=self.event,
            is_active=True
        )

    def test_event_list(self):
        """Test event listing endpoint"""
        url = reverse('event-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_event_detail(self):
        """Test event detail endpoint"""
        url = reverse('event-detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Event')

class SurveyAPITests(APITestCase):
    """Tests for survey-related endpoints"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date='2024-01-01T00:00:00Z',
            end_date='2024-01-02T00:00:00Z',
            location='Test Location',
            organizer=self.user
        )
        
        # Create test survey
        self.survey = Survey.objects.create(
            title='Test Survey',
            description='Test Survey Description',
            event=self.event,
            is_active=True
        )

    def test_survey_list(self):
        """Test survey listing endpoint"""
        url = reverse('survey-list', kwargs={'event_id': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_survey_detail(self):
        """Test survey detail endpoint"""
        url = reverse('survey-detail', kwargs={'pk': self.survey.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Survey')

