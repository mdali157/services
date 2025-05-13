from django.urls import path
from . import views

app_name = "receiving"

urlpatterns = [
    path('', views.add_receivings, name="add_receiving"),
]
