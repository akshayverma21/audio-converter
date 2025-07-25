"""
URL configuration for audio_converter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.urls import re_path
from audio_youtube import views


handler404 = 'audio_youtube.views.custom_404_view'

urlpatterns = [
    path('844794/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('', include('audio_youtube.urls')),  # Move converter to a different prefix
    path('pdf/', include('pdf_converter.urls')), 
    path('pdf/',include('file_converter.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_MEDIA_URL, document_root=settings.STATIC_MEDIA_ROOT)
    
