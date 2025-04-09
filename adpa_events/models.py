"""
Models for ADPA Event Management System

This module contains all database models for:
- Custom user authentication
- Event management system
- Event registration tracking
- Survey/questionnaire system
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        # Ensure required fields are set
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model implementing email-based authentication.
    
    Attributes:
        email (EmailField): Unique email address (used as username)
        first_name (CharField): User's first name
        last_name (CharField): User's last name
        is_staff (BooleanField): Designates staff/admin status
        is_active (BooleanField): Designates active status
        date_joined (DateTimeField): When user account was created
        is_member (BooleanField): Special membership status
        
    Relationships:
        - One-to-many with Event (as organizer)
        - One-to-many with EventRegistration
        - One-to-many with SurveyResponse
    """
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text="User's email address (used as username)"
    )
    first_name = models.CharField(
        _('first name'),
        max_length=30,
        help_text="User's first name"
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        help_text="User's last name"
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text="Designates whether the user can log into this admin site"
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
        help_text="Date when user account was created"
    )
    is_member = models.BooleanField(
        default=False,
        help_text="Designates special membership status"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Permission system fields with custom related names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="adpa_user_groups",
        related_query_name="adpa_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="adpa_user_permissions",
        related_query_name="adpa_user",
    )

    def __str__(self):
        """String representation using email"""
        return self.email

    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Event(models.Model):
    """
    An event that can be organized, registered for, and surveyed.
    
    Attributes:
        title (CharField): Event name (max 200 chars)
        description (TextField): Detailed event description
        start_date (DateTimeField): When event begins
        end_date (DateTimeField): When event ends
        location (CharField): Event venue (max 200 chars)
        organizer (ForeignKey): User who created the event
        created_at (DateTimeField): When event was created
        updated_at (DateTimeField): When event was last updated
        
    Relationships:
        - Many-to-one with User (organizer)
        - One-to-one with Survey (optional)
        - One-to-many with EventRegistration
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Name of the event (max 200 characters)"
    )
    description = models.TextField(
        help_text="Detailed description of the event"
    )
    start_date = models.DateTimeField(
        help_text="Date and time when event starts"
    )
    end_date = models.DateTimeField(
        help_text="Date and time when event ends"
    )
    location = models.CharField(
        max_length=200,
        help_text="Location/venue of the event"
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='adpa_organized_events',  # Changed to avoid clash
        help_text="User who organized this event"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this event was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this event was last updated"
    )

    def __str__(self):
        """String representation using event title"""
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['-start_date']


class EventRegistration(models.Model):
    """
    A user's registration for an event with attendance tracking.
    
    Attributes:
        event (ForeignKey): Related Event
        user (ForeignKey): Registered User
        registration_date (DateTimeField): When registration occurred
        attended (BooleanField): Whether user attended
        
    Relationships:
        - Many-to-one with Event
        - Many-to-one with User
        
    Constraints:
        - Unique together: (event, user) - prevents duplicate registrations
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='adpa_registrations',  # Changed to avoid clash
        help_text="Event being registered for"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='adpa_event_registrations',  # Changed to avoid clash
        help_text="User who registered"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the registration was made"
    )
    attended = models.BooleanField(
        default=False,
        help_text="Whether the user attended the event"
    )

    def __str__(self):
        """String representation combining user and event"""
        return f"{self.user.email} - {self.event.title}"

    class Meta:
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
        unique_together = ('event', 'user')
        ordering = ['-registration_date']


class Survey(models.Model):
    """
    A survey associated with an event to collect participant feedback.
    
    Attributes:
        event (OneToOneField): Related Event (optional)
        title (CharField): Survey title (max 200 chars)
        description (TextField): Detailed survey description
        is_active (BooleanField): Whether survey accepts responses
        created_at (DateTimeField): Auto-set on creation
        updated_at (DateTimeField): Auto-updated on save
        
    Relationships:
        - One-to-one with Event (optional)
        - One-to-many with Question
        - One-to-many with SurveyResponse
    """
    
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='adpa_survey',  # Changed to avoid clash
        null=True,
        blank=True,
        help_text="Event this survey is associated with (optional)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Title of the survey"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the survey"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the survey is currently accepting responses"
    )
    created_at = models.DateTimeField(
        default=timezone.now,  # Changed from auto_now_add to default
        help_text="When this survey was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this survey was last updated"
    )

    def __str__(self):
        """String representation using survey title"""
        return self.title

    class Meta:
        verbose_name = _('survey')
        verbose_name_plural = _('surveys')
        ordering = ['-created_at']


class Question(models.Model):
    """
    Individual questions within a survey.
    
    Attributes:
        survey (ForeignKey): Related Survey
        text (CharField): Question text (max 500 chars)
        question_type (CharField): Type of response expected
        is_required (BooleanField): Whether response is mandatory
        order (PositiveIntegerField): Display ordering
        
    Relationships:
        - Many-to-one with Survey
        - One-to-many with Choice
        - One-to-many with Answer
    """
    
    QUESTION_TYPES = (
        ('text', 'Text Answer'),
        ('radio', 'Single Choice'),
        ('checkbox', 'Multiple Choice'),
    )
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='adpa_questions',  # Changed to avoid clash
        help_text="Survey this question belongs to"
    )
    text = models.CharField(
        max_length=500,
        help_text="The question text (max 500 characters)"
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        help_text="Type of question/response expected"
    )
    is_required = models.BooleanField(
        default=True,
        help_text="Whether a response to this question is required"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordering position of the question in the survey"
    )

    def __str__(self):
        """String representation combining survey and question"""
        return f"{self.survey.title} - {self.text}"

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['order']


class Choice(models.Model):
    """
    A response choice for multiple-choice survey questions.
    
    Attributes:
        question (ForeignKey): Related Question
        text (CharField): Choice text (max 200 chars)
        order (PositiveIntegerField): Display ordering
        
    Relationships:
        - Many-to-one with Question
        - One-to-many with Answer (as choice_answer)
    """
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='adpa_choices',  # Changed to avoid clash
        help_text="Question this choice belongs to"
    )
    text = models.CharField(
        max_length=200,
        help_text="The choice text (max 200 characters)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordering position of the choice in the question"
    )

    def __str__(self):
        """String representation combining question and choice"""
        return f"{self.question.text} - {self.text}"

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"
        ordering = ['order']


class SurveyResponse(models.Model):
    """
    A user's submission of a completed survey.
    
    Attributes:
        survey (ForeignKey): Related Survey
        user (ForeignKey): Responding User
        submitted_at (DateTimeField): Auto-set on creation
        
    Relationships:
        - Many-to-one with Survey
        - Many-to-one with User
        - One-to-many with Answer
        
    Constraints:
        - Unique together: (survey, user) - prevents duplicate submissions
    """
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='adpa_responses',  # Changed to avoid clash
        help_text="Survey being responded to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='adpa_survey_responses',  # Changed to avoid clash
        help_text="User who submitted the response"
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this response was submitted"
    )

    def __str__(self):
        """String representation combining user and survey"""
        return f"{self.user.email} - {self.survey.title}"

    class Meta:
        verbose_name = "Survey Response"
        verbose_name_plural = "Survey Responses"
        unique_together = ('survey', 'user')
        ordering = ['-submitted_at']


class Answer(models.Model):
    """
    An individual answer to a survey question within a response.
    
    Attributes:
        response (ForeignKey): Related SurveyResponse
        question (ForeignKey): Related Question
        text_answer (TextField): Answer for text questions
        choice_answer (ForeignKey): Selected Choice for MC questions
        
    Relationships:
        - Many-to-one with SurveyResponse
        - Many-to-one with Question
        - Many-to-one with Choice (optional)
    """
    
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='adpa_answers',  # Changed to avoid clash
        help_text="Response this answer belongs to"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        help_text="Question being answered"
    )
    text_answer = models.TextField(
        blank=True,
        null=True,
        help_text="Answer for text-based questions"
    )
    choice_answer = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Selected choice for multiple-choice questions"
    )

    def __str__(self):
        """String representation of the answer content"""
        if self.text_answer:
            return f"Text answer: {self.text_answer[:50]}"
        if self.choice_answer:
            return f"Choice: {self.choice_answer.text}"
        return "Empty answer"

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"