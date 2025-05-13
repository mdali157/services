from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *


@login_required
def add_receivings(request):
    if request.method == 'POST':
        service_type = request.POST.get("service_type")
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        remarks = request.POST.get("remarks")
        description = request.POST.get("description")
        estimated_price = request.POST.get("estimated_price")
        # form = ReceivingForm()
    service_type = ServiceType.objects.all()
    return render(request, 'receiving/add_receiving.html', {'service_type': service_type})
