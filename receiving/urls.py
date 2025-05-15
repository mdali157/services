from django.urls import path
from . import views

app_name = "receiving"

urlpatterns = [
    path('', views.add_receivings, name="add_receiving"),
    path('print/<int:receiving_id>/', views.print_receiving_slip, name="print_receiving_slip"),
    path('delivery/', views.receiving_delivery, name='receiving_delivery'),
    path('search-receiving/', views.search_receiving, name="search_receiving"),
    path('search-customers/', views.search_customers, name="search_customer"),
    path('get/<int:service_no>/', views.get_receiving, name='get_receiving')
]
