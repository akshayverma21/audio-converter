from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *
from . import views



urlpatterns = [
    path('',views.home, name='home'),
    path('audio_converter', views.converter, name='audio_converter'),
]