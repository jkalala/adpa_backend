from django.urls import path
from .views import (
    EventList, EventDetail, SessionList, RegisterForEvent,
    DocumentList, SubmitSurveyResponse
)

urlpatterns = [
    path('events/', EventList.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    path('events/<int:event_id>/agenda/', SessionList.as_view(), name='session-list'),
    path('events/<int:event_id>/register/', RegisterForEvent.as_view(), name='event-register'),
    path('events/<int:event_id>/documents/', DocumentList.as_view(), name='document-list'),
    
   
]