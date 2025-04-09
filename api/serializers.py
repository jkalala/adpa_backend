from rest_framework import serializers
from .models import Event, EventRegistration, Question, Choice, Answer
from adpa_events.models import Survey, SurveyResponse, User
from django.contrib.auth import get_user_model
from members.models import Member, Project, Document

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_member')
        read_only_fields = ('id', 'is_member')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_member', 'profile_image']
        read_only_fields = ['email', 'is_member']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'

class EventRegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['user']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Survey
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    
    class Meta:
        model = SurveyResponse
        fields = '__all__'
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = SurveyResponse.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(response=response, **answer_data)
        
        return response

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    countries_list = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        countries_list = validated_data.pop('countries_list', None)
        project = super().create(validated_data)
        if countries_list:
            project.set_countries(countries_list)
        return project

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class EventDetailSerializer(serializers.ModelSerializer):
    registrations_count = serializers.IntegerField(read_only=True)
    is_registered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
