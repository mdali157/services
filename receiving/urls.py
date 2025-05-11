from django.urls import path
from . import views

app_name = "receivings"

urlpatterns = [
    path('', views.add_receivings, name="add_receivings"),
]
