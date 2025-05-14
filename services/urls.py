from django.contrib import admin
from django.urls import path, include
from .views import  homepage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="home"),
    path('receiving/', include('receiving.urls')),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),

]
