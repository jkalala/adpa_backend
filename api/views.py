"""
Django Views for the application API endpoints
Includes authentication, user management, and event/survey functionality
"""

from django.views.decorators.csrf import csrf_exempt  # Import CSRF exemption decorator
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import User, Event, EventRegistration, Question, Choice, Answer
from adpa_events.models import Survey, SurveyResponse  # Import Survey and SurveyResponse from adpa_events
from .serializers import (
    UserSerializer, 
    EventSerializer, 
    EventRegistrationSerializer,
    SurveySerializer, 
    QuestionSerializer, 
    ResponseSerializer,
    UserProfileSerializer,
    MemberSerializer,
    ProjectSerializer,
    DocumentSerializer,
    EventDetailSerializer
)
from rest_framework.reverse import reverse
import requests
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from utils.email import send_welcome_email, EmailLog
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Count
from django_filters import rest_framework as filters
from rest_framework.decorators import action  # Add this import at the top with other imports
from members.models import Member, Project, Document  # Add this import
from members.models import Event  # Make sure to import the correct Event model


class CSRFTokenView(APIView):
    """
    API endpoint to retrieve CSRF token for authenticated requests.
    This should be called before making any POST/PUT/DELETE requests.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access to get CSRF token

    def get(self, request):
        # Get the CSRF token from Django
        csrf_token = get_token(request)
        
        # Return the token in a JSON response
        return Response({
            'csrfToken': csrf_token
        }, status=status.HTTP_200_OK)

class GoogleLogin(APIView):
    """
    Handles Google OAuth2 login by verifying Google ID tokens
    and issuing JWT tokens for authenticated users
    """
    
    @csrf_exempt  # Exempt from CSRF since this is an API endpoint
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        """
        Process Google ID token and return JWT tokens
        """
        id_token = request.data.get('id_token')
        
        if not id_token:
            return Response(
                {'error': 'ID token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify token with Google's tokeninfo endpoint
            response = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
            )
            
            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid Google token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_data = response.json()
            
            # Verify audience matches our client ID
            if user_data.get('aud') != settings.GOOGLE_CLIENT_ID:
                return Response(
                    {'error': 'Invalid token audience'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user based on Google email
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data.get('given_name', ''),
                    'last_name': user_data.get('family_name', ''),
                    'username': user_data['email'].split('@')[0]
                }
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
                    'last_name': user.last_name
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class APIRootView(APIView):
    """
    Root API endpoint that shows available API routes
    """
    def get(self, request, format=None):
        return Response({
            'auth': {
                'login': reverse('login', request=request),
                'logout': reverse('logout', request=request),
                'register': reverse('register', request=request),
                'password-recovery': reverse('password-recovery', request=request),
                'token-refresh': reverse('token-refresh', request=request),
                'google': reverse('google_login', request=request),
            },
            'member': reverse('member', request=request),
            'user': reverse('user', request=request),
            'events': {
                'list': reverse('event-list', request=request),
                'detail': reverse('event-detail', kwargs={'pk': 1}, request=request).replace('/1', '/{id}'),
                'registration': reverse('event-registration-list', kwargs={'event_id': 1}, request=request).replace('/1', '/{id}'),
            },
            'surveys': {
                'list': reverse('survey-list', request=request),
                'detail': reverse('survey-detail', kwargs={'pk': 1}, request=request).replace('/1', '/{id}'),
                'responses': reverse('survey-response-list', kwargs={'survey_id': 1}, request=request).replace('/1', '/{id}'),
            },
        })

class SurveyView(APIView):
    """
    Handles survey listing and creation (admin only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all active surveys
        """
        surveys = Survey.objects.filter(is_active=True)
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        """
        Create new survey (admin only)
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can create surveys"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SurveyDetailView(APIView):
    """
    Handles individual survey operations
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        """
        Get survey details by ID
        """
        try:
            survey = Survey.objects.get(id=survey_id, is_active=True)
            serializer = SurveySerializer(survey)
            return Response(serializer.data)
        except Survey.DoesNotExist:
            return Response(
                {"error": "Survey not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class QuestionView(APIView):
    """
    Handles survey questions
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        """
        Get all questions for a survey
        """
        questions = Question.objects.filter(survey_id=survey_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class SubmitResponseView(APIView):
    """
    Handles survey responses submission
    """
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, survey_id):
        """
        Submit survey responses
        """
        try:
            survey = Survey.objects.get(id=survey_id, is_active=True)
        except Survey.DoesNotExist:
            return Response(
                {"error": "Survey not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check for duplicate submissions
        if SurveyResponse.objects.filter(survey=survey, user=request.user).exists():
            return Response(
                {"error": "You have already submitted this survey"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create survey response
        response_data = {
            "survey": survey.id,
            "user": request.user.id,
            "answers": request.data.get('answers', [])
        }

        serializer = ResponseSerializer(data=response_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MemberView(APIView):
    """
    Handles member-specific functionality and data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get member dashboard data
        """
        if not request.user.is_member:
            return Response(
                {"error": "You don't have member privileges"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Compile member dashboard data
        member_data = {
            "user": UserSerializer(request.user).data,
            "upcoming_events": self.get_upcoming_events(request.user),
            "event_registrations": self.get_event_registrations(request.user),
            "member_since": request.user.date_joined.strftime("%B %Y")
        }

        return Response(member_data)

    def get_upcoming_events(self, user):
        """
        Helper: Get upcoming events user hasn't registered for
        """
        registered_events = EventRegistration.objects.filter(
            user=user
        ).values_list('event_id', flat=True)
        
        upcoming_events = Event.objects.filter(
            start_date__gte=timezone.now()
        ).exclude(
            id__in=registered_events
        ).order_by('start_date')[:5]
        
        return EventSerializer(upcoming_events, many=True).data

    def get_event_registrations(self, user):
        """
        Helper: Get user's event registrations
        """
        registrations = EventRegistration.objects.filter(
            user=user,
            event__start_date__gte=timezone.now()
        ).select_related('event').order_by('event__start_date')
        
        return [
            {
                "event": EventSerializer(reg.event).data,
                "registration_date": reg.registration_date,
                "attended": reg.attended
            }
            for reg in registrations
        ]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        """
        Handle member actions (event registration)
        """
        action = request.data.get('action')
        
        if action == 'register_event':
            event_id = request.data.get('event_id')
            try:
                event = Event.objects.get(id=event_id)
                EventRegistration.objects.create(
                    user=request.user,
                    event=event
                )
                return Response({"success": "Registered for event successfully"})
            except Event.DoesNotExist:
                return Response(
                    {"error": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(
            {"error": "Invalid action"},
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    """
    Handles user logout by blacklisting refresh tokens
    """
    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        """
        Blacklist the refresh token
        """
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class PasswordRecoveryView(APIView):
    """
    Handles password recovery requests
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        """
        Initiate password recovery process
        """
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'No user with this email exists'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate and store recovery token
        token = get_random_string(length=32)
        user.password_reset_token = token
        user.password_reset_expires = timezone.now() + timedelta(hours=24)
        user.save()

        # Send recovery email
        recovery_link = f"{settings.FRONTEND_URL}/password-reset/{token}/"
        send_mail(
            'Password Recovery Request',
            f'Click this link to reset your password: {recovery_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {'message': 'Password recovery email sent'},
            status=status.HTTP_200_OK
        )

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh endpoint
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        """
        Refresh access token using valid refresh token
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({
            'access': serializer.validated_data['access'],
            'refresh': request.data.get('refresh')  # Return the same refresh token
        }, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    """
    Handles password reset with valid token
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return Response({
                'message': 'If an account exists with this email, a password reset link will be sent.'
            })

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset link
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        
        # Send email
        context = {
            'user': user,
            'reset_url': reset_url
        }
        
        html_message = render_to_string('email/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            'Reset Your Password',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )
        
        return Response({
            'message': 'Password reset email has been sent.'
        })

class PasswordResetConfirmView(APIView):
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        
        if not all([uid, token, password]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response({
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not default_token_generator.check_token(user, token):
            return Response({
                'error': 'Invalid or expired reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(password)
        user.save()
        
        return Response({
            'message': 'Password has been reset successfully'
        })

class RegisterView(APIView):
    """
    Handles new user registration
    """
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def post(self, request):
        """
        Register new user
        """
        # Extract registration data
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        # Validate required fields
        if not all([email, password, first_name, last_name]):
            return Response(
                {'error': 'All fields (email, password, first_name, last_name) are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing user
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create new user (non-member by default)
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_member=False
            )
            
            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                # Log the error but don't prevent registration
                print(f"Failed to send welcome email: {str(e)}")
            
            return Response(
                {
                    'message': 'Registration successful. Please wait for membership approval.',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    """
    Handles user authentication and JWT token generation
    """
    permission_classes = [AllowAny]

    def verify_recaptcha(self, token):
        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': token
            })
            result = response.json()
            return result.get('success', False)
        except Exception as e:
            print(f"reCAPTCHA verification error: {str(e)}")
            return False

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        recaptcha_token = request.data.get('g_recaptcha_response')

        # Validate required fields
        if not all([email, password]):
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify reCAPTCHA
        if not recaptcha_token:
            return Response(
                {'error': 'reCAPTCHA verification is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not self.verify_recaptcha(recaptcha_token):
            return Response(
                {'error': 'reCAPTCHA verification failed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserView(APIView):
    """
    Handles user profile data
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get current user profile
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class EventList(generics.ListCreateAPIView):
    """
    Handles event listing and creation (members only)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter events based on user membership
        """
        if self.request.user.is_member:
            return Event.objects.all()
        return Event.objects.none()

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def perform_create(self, serializer):
        """
        Set event organizer to current user
        """
        serializer.save(organizer=self.request.user)

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles individual event operations
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter events based on user membership
        """
        if self.request.user.is_member:
            return Event.objects.all()
        return Event.objects.none()

def track_email_open(request, email_id):
    """Track email opens using a 1x1 transparent pixel."""
    try:
        email_log = EmailLog.objects.get(email_id=email_id)
        if not email_log.opened_at:
            email_log.opened_at = timezone.now()
            email_log.save()
    except EmailLog.DoesNotExist:
        pass

    # Return a 1x1 transparent pixel
    pixel = bytes.fromhex('47494638396101000100800000dbdbdb00000021f90401000000002c00000000010001000002024401003b')
    return HttpResponse(pixel, content_type='image/gif')

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully'})

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = {
            'total_members': Member.objects.count(),
            'active_members': Member.objects.filter(status='Active').count(),
            'observers': Member.objects.filter(status='Observer').count(),
            'countries_represented': Member.objects.values('country').distinct().count()
        }
        return Response(stats)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        project = self.get_object()
        progress = request.data.get('progress')
        if progress is not None and 0 <= int(progress) <= 100:
            project.progress = progress
            project.save()
            return Response({'message': 'Progress updated successfully'})
        return Response(
            {'error': 'Invalid progress value'},
            status=status.HTTP_400_BAD_REQUEST
        )

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Document.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    @action(detail=True, methods=['post'])
    def increment_downloads(self, request, pk=None):
        document = self.get_object()
        document.download_count += 1
        document.save()
        return Response({'download_count': document.download_count})

class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_attended(self, request, pk=None):
        registration = self.get_object()
        registration.attended = True
        registration.save()
        return Response({'message': 'Attendance marked'})

class EventFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="start_date", lookup_expr='gte')
    max_date = filters.DateTimeFilter(field_name="start_date", lookup_expr='lte')
    event_type = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Event
        fields = ['event_type', 'is_public', 'location']

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EventFilter
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'title']

    def get_queryset(self):
        queryset = Event.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        return queryset.order_by('start_date')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            return Response(
                {'error': 'Already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        EventRegistration.objects.create(event=event, user=request.user)
        return Response({'message': 'Registration successful'})