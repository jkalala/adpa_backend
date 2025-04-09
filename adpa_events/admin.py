from django.contrib import admin
from .models import (
    User,
    Event,
    EventRegistration,
    Survey,
    Question,
    Choice,
    SurveyResponse,
    Answer
)
# Register your models here.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(SurveyResponse)
admin.site.register(Answer)
