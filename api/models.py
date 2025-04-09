"""
Django Models for Survey and Event Management System

This module contains all database models for:
- Custom user authentication
- Event management
- Survey creation and response collection
- Event registration tracking

All models follow Django's model best practices with proper relationships,
field types, and meta options.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from adpa_events.models import (
    Event,
    Survey,
    Question,
    Choice,
    SurveyResponse,
    Answer
)

# Get the custom User model to use in relationships
User = get_user_model()

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
        related_name='api_registrations',  # Changed to avoid clash
        help_text="Event being registered for"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_event_registrations',  # Changed to avoid clash
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


class UserManager(BaseUserManager):
    """
    Custom manager for the User model with email-based authentication.
    
    Methods:
        create_user: Creates and saves a regular user
        create_superuser: Creates and saves a superuser
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        
        Args:
            email (str): User's email address
            password (str): User's password
            **extra_fields: Additional user attributes
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        
        Args:
            email (str): Superuser's email address
            password (str): Superuser's password
            **extra_fields: Additional superuser attributes
            
        Returns:
            User: The created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_member', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the unique identifier.
    
    Attributes:
        email (EmailField): Unique user identifier
        first_name (CharField): User's first name
        last_name (CharField): User's last name
        is_staff (BooleanField): Admin access flag
        is_active (BooleanField): Account active flag
        date_joined (DateTimeField): Account creation date
        is_member (BooleanField): Special membership flag
        
    Methods:
        get_full_name: Returns the user's full name
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
        related_name="api_user_groups",
        related_query_name="api_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="api_user_permissions",
        related_query_name="api_user",
    )

    def __str__(self):
        """String representation using email"""
        return self.email

    def get_full_name(self):
        """Returns the user's full name"""
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"