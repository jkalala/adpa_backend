import uuid
from django.db import models

class EmailLog(models.Model):
    email_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'utils'
        ordering = ['-sent_at']
        
    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})" 