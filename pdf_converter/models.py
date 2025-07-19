from django.db import models
from django.contrib.auth.models import User
from slugify import slugify
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
# Create your models here.


class FileConversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  
    original_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    converted_file = models.FileField(upload_to='converted/', null=True, blank=True)
    input_format = models.CharField(max_length=10)
    output_format = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')  
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.original_file.name} -> {self.output_format}"
    

class Article(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True, blank=True)
    title=models.CharField(max_length=200)
    content=CKEditor5Field(config_name='default')
    article_image = models.URLField(blank=True, default='')
    created_at=models.DateTimeField(auto_now_add=True)
    slug=models.SlugField(unique=True, max_length=255)

    def save(self, *args, **kwargs):
     if not self.slug:
        self.slug = slugify(self.title)
        while Article.objects.filter(slug=self.slug).exists():
            self.slug = f"{slugify(self.title)}-{counter}"
            counter += 1
     super().save(*args, **kwargs)
    
    def __str__(self):
         return self.title


