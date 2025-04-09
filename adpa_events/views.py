from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Event, EventRegistration, Survey, SurveyResponse
from .serializers import (
    EventSerializer,
    EventRegistrationSerializer,
    SurveySerializer,
    QuestionSerializer,
    ChoiceSerializer,
    ResponseSerializer
)

User = get_user_model()

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EventList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

class EventDetail(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

class EventRegistrationList(generics.ListCreateAPIView):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EventRegistrationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

class SurveyList(generics.ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

class SurveyResponseList(generics.ListCreateAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SurveyResponseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

@csrf_exempt
@require_http_methods(["POST"])
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if EventRegistration.objects.filter(event=event, user=user).exists():
        return JsonResponse({'error': 'Already registered'}, status=400)

    registration = EventRegistration.objects.create(event=event, user=user)
    return JsonResponse({'message': 'Registration successful', 'id': registration.id})

@login_required
def submit_survey_response(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    user = request.user

    if SurveyResponse.objects.filter(survey=survey, user=user).exists():
        return JsonResponse({'error': 'Already submitted'}, status=400)

    response = SurveyResponse.objects.create(survey=survey, user=user)
    return JsonResponse({'message': 'Response submitted', 'id': response.id})