from django.urls import path
from .views import (
    DashboardMetricsView,
    MemberListView,
    ProjectListView,
    DocumentListView,
    EventListView
)

urlpatterns = [
    path('member/data/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('members/', MemberListView.as_view(), name='member-list'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('events/', EventListView.as_view(), name='event-list'),
]