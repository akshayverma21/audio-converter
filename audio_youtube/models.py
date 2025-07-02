from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class AudioConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Optional: support anonymous users
    original_file = models.FileField(upload_to='uploads/')
    converted_file = models.FileField(upload_to='converted/', null=True, blank=True)
    input_format = models.CharField(max_length=10)
    output_format = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')  # could be 'pending', 'processing', 'completed', 'failed'
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.original_file.name} -> {self.output_format}"