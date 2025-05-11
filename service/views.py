from django.shortcuts import render
from .models import Service

def service_list(request):
    services = Service.objects.all()
    print("SERVICES:", list(services))  # Debug log
    return render(request, 'home_page.html', {'services': services})
