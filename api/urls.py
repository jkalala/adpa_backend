"""
URL Configuration for API Endpoints

This module defines all URL routes for the application's API endpoints,
including authentication, user management, and feature-specific routes.

All URLs are namespaced and follow RESTful conventions where applicable.
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    GoogleLogin,
    CustomTokenRefreshView,
    APIRootView,
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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', EventRegistrationViewSet, basename='registration')

schema_view = get_schema_view(
    openapi.Info(
        title="ADPA API",
        default_version='v1',
        description="API documentation for ADPA Event Hub",
        terms_of_service="https://www.adpa.org/terms/",
        contact=openapi.Contact(email="contact@adpa.org"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # ========================
    # Authentication Endpoints
    # ========================
    
    # API Root View - Entry point documentation
    path('', APIRootView.as_view(), name='api-root'),
    
    # Session-based Authentication
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/csrf/', CSRFTokenView.as_view(), name='get_csrf_token'),
    
    # Token-based Authentication
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # Password Management
    path('auth/password-recovery/', PasswordRecoveryView.as_view(), name='password-recovery'),
    
    # ====================
    # User Management
    # ====================
    
    # User Registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # User Profile
    path('user/', UserView.as_view(), name='user'),
    
    # ====================
    # Feature Endpoints
    # ====================
    
    # Member Management
    path('member/', MemberView.as_view(), name='member'),
    
    # Event Management
    path('events/', EventList.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    
    # Event Registration
    path('events/<int:event_id>/register/', EventRegistrationList.as_view(), name='event-registration-list'),
    path('registrations/<int:pk>/', EventRegistrationDetail.as_view(), name='event-registration-detail'),
    
    # Survey Management
    path('surveys/', SurveyList.as_view(), name='survey-list'),
    path('surveys/<int:pk>/', SurveyDetail.as_view(), name='survey-detail'),
    
    # Survey Responses
    path('surveys/<int:survey_id>/responses/', SurveyResponseList.as_view(), name='survey-response-list'),
    path('responses/<int:pk>/', SurveyResponseDetail.as_view(), name='survey-response-detail'),
    
    # ====================
    # Third-Party Auth
    # ====================
    
    # Google OAuth2 Integration
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    
    # Email Tracking
    path('email/track/<uuid:email_id>.png', track_email_open, name='track_email_open'),
    
    # Password Reset
    path('auth/password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Include the router URLs
    path('', include(router.urls)),
    
    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]