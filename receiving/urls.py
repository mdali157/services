from django.urls import path
from . import views

app_name = "receiving"

urlpatterns = [
    path('', views.add_receivings, name="add_receiving"),
    path('print/<int:receiving_id>/', views.print_receiving_slip, name="print_receiving_slip"),
]
