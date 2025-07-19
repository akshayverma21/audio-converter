from django.shortcuts import render
import json 
from PIL import Image
import io
from django.urls import path
from . import views

urlpatterns = [
    path('file-to-pdf',views.convert_document,name='convert_document'),
    path('get-formats/', views.get_allowed_formats, name='get_allowed_formats'),
]