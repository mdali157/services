from django.urls import path
from . import views

app_name = "casting"

urlpatterns = [
    path('', views.add_casting, name="add_casting"),
    path('search/karate/', views.search_karate, name="search_karate"),
    path('search/color/', views.search_casting, name="search_casting"),
    path('print/<int:casting_id>/', views.print_casting_slip, name="print_casting_slip"),
    path('delivery/print/<int:casting_id>/', views.casting_flask_print_slip, name="casting_flask_print_slip"),
    path('flask', views.all_flask, name="all_flask"),
    path('add/flask', views.add_flask, name="add_flask"),
    path('flask/<int:flask_id>/update/', views.update_flask, name='update_flask'),
    path('all/', views.all_casting, name='all_casting'),
    path('<int:casting_id>/update/', views.update_casting, name="update_casting")

]
