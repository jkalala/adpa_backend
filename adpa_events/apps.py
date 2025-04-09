# adpa_events/apps.py
from django.apps import AppConfig

class AdpaEventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adpa_events'
    
    def ready(self):
        # Import signals or other startup code here if needed
        pass