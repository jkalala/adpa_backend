from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import json

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.login_url = reverse('login')
        
        # Create test user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_successful(self):
        """Test successful login with correct credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'g_recaptcha_response': 'test_token'  # Mock token for testing
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass',
            'g_recaptcha_response': 'test_token'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email_format(self):
        """Test login with invalid email format"""
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'g_recaptcha_response': 'test_token'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PasswordResetTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_password_reset_request(self):
        """Test password reset request"""
        data = {'email': self.user.email}
        response = self.client.post(self.password_reset_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset Your Password', mail.outbox[0].subject)

    def test_password_reset_invalid_email(self):
        """Test password reset with invalid email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Don't reveal user existence
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Generate reset token
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        data = {
            'uid': uid,
            'token': token,
            'password': 'newpass123'
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token"""
        data = {
            'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'token': 'invalid-token',
            'password': 'newpass123'
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpass123')) 