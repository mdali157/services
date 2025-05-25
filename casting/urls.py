from django.urls import path
from . import views

app_name = "casting"

urlpatterns = [
    path('', views.add_casting, name="add_casting"),
    path('search/karate/', views.search_karate, name="search_karate"),
    path('search/color/', views.search_casting, name="search_casting"),
    path('print/<int:casting_id>/', views.print_casting_slip, name="print_casting_slip"),

]
