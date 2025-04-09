"""
Test Cases for ADPA Events API

Comprehensive tests for all API endpoints with proper setup and documentation.
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import User, Event, Session, Registration, Document, Survey, SurveyResponse

class BaseAPITestCase(APITestCase):
    """
    Base test case with common setup for all API tests.
    Creates test users, events, and related objects.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create initial test data shared across all test methods"""
        # Create regular user
        cls.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create admin user
        cls.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create current (upcoming) event
        cls.current_event = Event.objects.create(
            title='Current Event',
            description='Test description',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            location='Test Location',
            organizer=cls.user
        )
        
        # Create past event
        cls.past_event = Event.objects.create(
            title='Past Event',
            description='Test description',
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1),
            location='Past Location',
            organizer=cls.user
        )
        
        # Create session for current event
        cls.session = Session.objects.create(
            name='Test Session',
            event=cls.current_event,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Create document for current event (without uploaded_by)
        cls.document = Document.objects.create(
            title='Test Document',
            event=cls.current_event,
            file='documents/test.pdf',
            is_public=True
        )
        
        # Create survey for current event
        cls.survey = Survey.objects.create(
            title='Test Survey',
            event=cls.current_event,
            is_active=True
        )

    def setUp(self):
        """Run before each test method"""
        self.client.force_authenticate(user=self.user)


class UserAPITests(BaseAPITestCase):
    """Tests for user authentication and management endpoints"""
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EventAPITests(BaseAPITestCase):
    """Tests for event-related endpoints"""
    
    def test_event_list(self):
        """Test event listing endpoint"""
        url = reverse('event-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SessionAPITests(BaseAPITestCase):
    """Tests for session-related endpoints"""
    
    def test_session_list(self):
        """Test session listing endpoint"""
        url = reverse('session-list', kwargs={'event_id': self.current_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RegistrationAPITests(BaseAPITestCase):
    """Tests for event registration endpoints"""
    
    def test_event_registration(self):
        """Test event registration endpoint"""
        url = reverse('register-for-event', kwargs={'event_id': self.current_event.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DocumentAPITests(BaseAPITestCase):
    """Tests for document-related endpoints"""
    
    def test_document_list(self):
        """Test document listing endpoint"""
        url = reverse('document-list', kwargs={'event_id': self.current_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SurveyAPITests(BaseAPITestCase):
    """Tests for survey-related endpoints"""
    
    def test_survey_list(self):
        """Test survey listing endpoint"""
        url = reverse('survey-list', kwargs={'event_id': self.current_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SurveyResponseAPITests(BaseAPITestCase):
    """Tests for survey response endpoints"""
    
    def test_survey_response(self):
        """Test survey response submission"""
        url = reverse('submit-survey-response', kwargs={'survey_id': self.survey.pk})
        data = {'answers': [{'question_id': 1, 'answer': 'Test'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)