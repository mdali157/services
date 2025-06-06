from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import homepage
from casting.views import report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="home"),
    path('receiving/', include('receiving.urls')),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('casting/', include('casting.urls')),
    path('reports/', report, name="report")

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
