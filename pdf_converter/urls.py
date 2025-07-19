from django.shortcuts import render
import json 
from PIL import Image
import io
from django.urls import path
from . import views

urlpatterns = [
    path('image-to-pdf/', views.image_converter, name='image_to_pdf'),
    path('articles/<slug:slug>', views.article_view, name='article_detail'),
]