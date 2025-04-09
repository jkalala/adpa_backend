from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Member, Project, Document, Event
from .serializers import (
    MemberSerializer, 
    ProjectSerializer,
    DocumentSerializer,
    EventSerializer,
    DashboardMetricsSerializer
)
from django.db.models import Count
from datetime import datetime

class DashboardMetricsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardMetricsSerializer

    def get(self, request):
        metrics = {
            'member_count': Member.objects.filter(status='Active').count(),
            'observer_count': Member.objects.filter(status='Observer').count(),
            'annual_budget': 8500000,
            'active_projects': Project.objects.filter(status='Active').count(),
            'compliance_rate': 87,
            'growth_data': list(
                Member.objects.values('since')
                .annotate(count=Count('id'))
                .order_by('since')
            ),
            'recent_activities': [
                {
                    'id': member.id,
                    'text': f"{member.country} joined ADPA",
                    'date': member.since
                } 
                for member in Member.objects.order_by('-since')[:5]
            ]
        }
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)

class MemberListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class ProjectListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class DocumentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class EventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(
            start_date__gte=datetime.now()
        ).order_by('start_date')[:10]