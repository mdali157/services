from django.contrib import admin
from django.urls import path, include
from .import views
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout_page, name='logout'),
    path('login/', views.login_page, name='login'),

]