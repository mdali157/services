from django.urls import path
from . import views

app_name = "receiving"

urlpatterns = [
    path('', views.add_receivings, name="add_receiving"),
    path('print/<int:receiving_id>/', views.print_receiving_slip, name="print_receiving_slip"),
    path('<int:service_no>/', views.get_receiving_and_update_delivery_fields, name='get_receiving_and_update_delivery_fields'),
    path('all/', views.get_all_receiving, name='all_receiving')

]
