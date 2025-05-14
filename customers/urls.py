from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path('', views.search_customers, name="search_customer"),
]
