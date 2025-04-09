from rest_framework import serializers
from .models import Member, Project, Document, Event

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_countries(self, obj):
        return obj.get_countries_list()

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class DashboardMetricsSerializer(serializers.Serializer):
    member_count = serializers.IntegerField()
    observer_count = serializers.IntegerField()
    annual_budget = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_projects = serializers.IntegerField()
    compliance_rate = serializers.IntegerField()
    growth_data = serializers.ListField()
    recent_activities = serializers.ListField()