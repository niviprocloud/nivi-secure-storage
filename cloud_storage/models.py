from django.db import models
from django.contrib.auth.models import User
import os
import uuid

class EncryptedFile(models.Model):
    """Model for storing encrypted files uploaded by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encrypted_files')
    original_filename = models.CharField(max_length=255)
    encrypted_filename = models.CharField(max_length=255, unique=True)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    encryption_key = models.BinaryField()
    iv = models.BinaryField()  # Initialization vector for encryption
    upload_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.original_filename} (Uploaded by {self.user.username})"
    
    def get_file_path(self):
        """Returns the path to the encrypted file on disk"""
        from django.conf import settings
        return os.path.join(settings.ENCRYPTED_FILES_ROOT, str(self.user.id), self.encrypted_filename)
    
    def save(self, *args, **kwargs):
        """Override save to generate a unique encrypted filename if not provided"""
        if not self.encrypted_filename:
            self.encrypted_filename = f"{uuid.uuid4().hex}.enc"
        super().save(*args, **kwargs)

class SecurityLog(models.Model):
    """Model for logging security events and potential threats"""
    LOG_LEVELS = (
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )
    
    EVENT_TYPES = (
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('UPLOAD', 'File Upload'),
        ('DOWNLOAD', 'File Download'),
        ('DELETE', 'File Delete'),
        ('THREAT', 'Security Threat'),
        ('SYSTEM', 'System Event'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    file = models.ForeignKey(EncryptedFile, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_level_display()}: {self.get_event_type_display()} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
