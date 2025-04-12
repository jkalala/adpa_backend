"""
Django API Views for Authentication and User Management

This module contains all API endpoints for:
- User authentication (login, logout)
- User registration
- Password recovery and reset
- Google OAuth integration
- User profile management
- Token handling

All views follow RESTful conventions and include:
- Proper authentication
- Input validation
- Detailed error responses
- Comprehensive documentation
"""

from datetime import timedelta
import re
import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView

User = get_user_model()

class CSRFTokenView(APIView):
    """
    API endpoint to retrieve CSRF token for authenticated requests.
    
    This should be called before making any POST/PUT/DELETE requests
    that require CSRF protection.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieve CSRF token
        
        Returns:
            Response: JSON containing the CSRF token
            Example: {'csrfToken': 'token_value'}
        """
        return Response(
            {'csrfToken': get_token(request)},
            status=status.HTTP_200_OK
        )

class LoginView(APIView):
    """
    Handles user authentication with email/password
    
    Methods:
        POST: Authenticate user and return JWT tokens
        
    Request Body:
        email: string (required)
        password: string (required)
        
    Returns:
        On success: JWT tokens and user data
        On failure: Error message with status code
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate required fields
        if not email or not password:
            return Response(
                {'error': 'Both email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is inactive'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff
            }
        })

class RegisterView(APIView):
    """
    Handles new user registration
    
    Methods:
        POST: Register a new user
        
    Request Body:
        email: string (required)
        password: string (required)
        first_name: string (required)
        last_name: string (required)
        
    Returns:
        On success: User data and success message
        On failure: Error message with status code
    """
    permission_classes = [AllowAny]

    def validate_password(self, password):
        """Validate password meets complexity requirements"""
        if len(password) < 8:
            return False, 'Password must be at least 8 characters'
        if not re.search(r'[A-Z]', password):
            return False, 'Password must contain an uppercase letter'
        if not re.search(r'[a-z]', password):
            return False, 'Password must contain a lowercase letter'
        if not re.search(r'[0-9]', password):
            return False, 'Password must contain a number'
        return True, ''

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        # Validate required fields
        if not all([email, password, first_name, last_name]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password strength
        is_valid, error = self.validate_password(password)
        if not is_valid:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing user
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create new user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True  # Or False if email verification required
            )
            
            return Response(
                {
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordRecoveryView(APIView):
    """
    Handles password recovery requests
    
    Methods:
        POST: Initiate password recovery process
        
    Request Body:
        email: string (required)
        
    Returns:
        Response: Success message or error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether user exists
            return Response(
                {'message': 'If an account exists, a recovery link was sent'},
                status=status.HTTP_200_OK
            )

        # Generate token and reset link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Send email
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_url}\n'
            f'This link will expire in 24 hours.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {'message': 'Password reset email sent if account exists'},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    """
    Handles password reset confirmation
    
    Methods:
        POST: Confirm password reset with valid token
        
    Request Body:
        uid: string (required)
        token: string (required)
        password: string (required)
        
    Returns:
        Response: Success message or error
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        
        if not all([uid, token, password]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(password)
        user.save()
        
        return Response(
            {'message': 'Password has been reset successfully'},
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    """
    Handles user logout by blacklisting refresh tokens
    
    Methods:
        POST: Blacklist the refresh token
        
    Request Body:
        refresh: string (required) - The refresh token to blacklist
        
    Returns:
        Response: Success message or error
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomTokenRefreshView(APIView):
    """
    Handles JWT token refresh
    
    Methods:
        POST: Refresh an access token
        
    Request Body:
        refresh: string (required) - Valid refresh token
        
    Returns:
        Response: New access token and original refresh token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        except TokenError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 authentication endpoint
    
    Methods:
        POST: Authenticate user with Google OAuth2 token
        
    Request Body:
        access_token: string (required) - Google OAuth2 access token
        id_token: string (optional) - Google ID token
        
    Returns:
        On success: JWT tokens and user data
        On failure: Error message with status code
        
    Notes:
        - Requires proper Google OAuth2 setup in Django settings
        - Uses django-allauth for social authentication
        - Automatically creates new users if they don't exist
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = getattr(settings, 'GOOGLE_CALLBACK_URL', None)

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            # Customize the response data if needed
            if response.status_code == status.HTTP_200_OK:
                user = request.user
                refresh = RefreshToken.for_user(user)
                response.data.update({
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff
                    }
                })
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Google authentication failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(APIView):
    """
    Handles user profile data
    
    Methods:
        GET: Retrieve current user's profile
        PATCH: Update current user's profile
        
    Returns:
        User profile data or error message
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined
        })

    def patch(self, request):
        user = request.user
        data = request.data
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        try:
            user.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        except Exception as e:
            return Response(
                {'error': f'Profile update failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )