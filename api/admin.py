from django.contrib import admin
from utils.email import EmailLog

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('email_id', 'recipient', 'subject', 'template_name', 'sent_at', 'status', 'opened_at')
    list_filter = ('status', 'template_name', 'sent_at')
    search_fields = ('recipient', 'subject', 'email_id')
    readonly_fields = ('email_id', 'sent_at', 'opened_at', 'clicked_at')
    
    def has_add_permission(self, request):
        return False
