from django.contrib import admin
from .models import EncryptedFile, SecurityLog

@admin.register(EncryptedFile)
class EncryptedFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'file_size', 'upload_date', 'last_accessed')
    list_filter = ('upload_date', 'last_accessed')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('encrypted_filename', 'encryption_key', 'iv')
    date_hierarchy = 'upload_date'

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'event_type', 'level', 'ip_address')
    list_filter = ('event_type', 'level', 'timestamp')
    search_fields = ('message', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'ip_address')
    date_hierarchy = 'timestamp'
