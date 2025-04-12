"""
URL Configuration for ADPA Backend API

This module defines all API endpoints for:
- Authentication (login, logout, registration)
- User management
- Event management
- Survey functionality
- API documentation

All endpoints follow RESTful conventions and include:
- Proper authentication requirements
- Clear URL naming
- Comprehensive documentation
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import all necessary views
from .views import (
    GoogleLogin,
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    RegisterView,
    PasswordRecoveryView,
    UserView,
    MemberView,
    CSRFTokenView,
    EventList,
    EventDetail,
    track_email_open,
    PasswordResetView,
    PasswordResetConfirmView,
    UserProfileViewSet,
    MemberViewSet,
    ProjectViewSet,
    DocumentViewSet,
    EventRegistrationViewSet,
    EventViewSet
)
from adpa_events.views import (
    SurveyList,
    SurveyDetail,
    EventRegistrationList,
    EventRegistrationDetail,
    SurveyResponseList,
    SurveyResponseDetail
)

# Initialize DefaultRouter for ViewSets
router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', EventRegistrationViewSet, basename='registration')

# API Root View - Shows available endpoints
class APIRootView(APIView):
    """
    API Root Endpoint
    
    Provides hyperlinks to all available API endpoints.
    Useful for API discovery and documentation.
    
    Methods:
        GET: Returns a dictionary of all available API endpoints
    """
    def get(self, request, format=None):
        return Response({
            'authentication': {
                'login': reverse('login', request=request),
                'logout': reverse('logout', request=request),
                'register': reverse('register', request=request),
                'password-recovery': reverse('password-recovery', request=request),
                'token-refresh': reverse('token-refresh', request=request),
                'google-oauth': reverse('google_login', request=request),
                'csrf-token': reverse('get_csrf_token', request=request),
            },
            'user-management': {
                'current-user': reverse('user', request=request),
                'user-profiles': reverse('user-list', request=request),
            },
            'events': {
                'list': reverse('event-list', request=request),
                'detail': reverse('event-detail', kwargs={'pk': 1}, request=request).replace('/1', '/{id}'),
            },
            'surveys': {
                'list': reverse('survey-list', request=request),
                'detail': reverse('survey-detail', kwargs={'pk': 1}, request=request).replace('/1', '/{id}'),
                'responses': reverse('survey-response-list', kwargs={'survey_id': 1}, request=request).replace('/1', '/{id}'),
            },
            'documentation': {
                'swagger': reverse('schema-swagger-ui', request=request),
                'redoc': reverse('schema-redoc', request=request),
            }
        })

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="ADPA API",
        default_version='v1',
        description="Comprehensive API documentation for ADPA Event Hub",
        terms_of_service="https://www.adpa.org/terms/",
        contact=openapi.Contact(email="api-support@adpa.org"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# URL Patterns
urlpatterns = [
    # ========================
    # Core API Endpoints
    # ========================
    path('', APIRootView.as_view(), name='api-root'),
    
    # ========================
    # Authentication Endpoints
    # ========================
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/csrf/', CSRFTokenView.as_view(), name='get_csrf_token'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/password-recovery/', PasswordRecoveryView.as_view(), name='password-recovery'),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # ====================
    # User Management
    # ====================
    path('user/', UserView.as_view(), name='user'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # ====================
    # Member Management
    # ====================
    path('member/', MemberView.as_view(), name='member'),
    
    # ====================
    # Event Management
    # ====================
    path('events/', EventList.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    path('events/<int:event_id>/register/', EventRegistrationList.as_view(), name='event-registration-list'),
    
    # ====================
    # Survey Management
    # ====================
    path('surveys/', SurveyList.as_view(), name='survey-list'),
    path('surveys/<int:pk>/', SurveyDetail.as_view(), name='survey-detail'),
    path('surveys/<int:survey_id>/responses/', SurveyResponseList.as_view(), name='survey-response-list'),
    
    # ====================
    # Email Tracking
    # ====================
    path('email/track/<uuid:email_id>.png', track_email_open, name='track_email_open'),
    
    # ====================
    # Documentation
    # ====================
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    
    # Include all router URLs (for ViewSets)
    path('', include(router.urls)),
]

# ====================
# URL Naming Convention
# ====================
"""
Authentication:
- login: auth/login/
- logout: auth/logout/
- token-refresh: auth/token/refresh/
- password-recovery: auth/password-recovery/

User Management:
- current-user: user/
- register: register/

Event Management:
- list: events/
- detail: events/<id>/
- registration: events/<id>/register/

Survey Management:
- list: surveys/
- detail: surveys/<id>/
- responses: surveys/<id>/responses/

Documentation:
- swagger: swagger/
- redoc: redoc/
"""