from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.service_list, name='service_list'),
]
