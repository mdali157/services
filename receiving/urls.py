from django.urls import path
from . import views

app_name = 'receiving'

urlpatterns = [
    path('add_receivings/', views.add_receivings, name="add_receivings"),
    path('customer-autocomplete/', views.customer_autocomplete, name='customer_autocomplete'),
]
