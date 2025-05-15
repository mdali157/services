import base64
import uuid
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import *


@login_required
def add_receivings(request):
    if request.method == 'POST':
        service_type = request.POST.get("service_type")
        customer_name = request.POST.get("customer_name").strip()
        customer_phone = request.POST.get("customer_phone").strip()
        remarks = request.POST.get("remarks")
        description = request.POST.get("description")
        estimated_price = request.POST.get("estimated_price")
        captured_image_data = request.POST.get("captured_image")  # from hidden input

        # Get or create customer
        try:
            customer = Customer.objects.get(name=customer_name, phone_number=customer_phone)
        except Customer.DoesNotExist:
            customer = None

        if not customer:
            customer = Customer.objects.create(phone_number=customer_phone, name=customer_name, added_by=request.user)

        # Prepare Receiving instance
        receiving = Receiving(
            service_type=service_type,
            description=description,
            remarks=remarks,
            estimated_price=estimated_price,
            actual_price=0,
            created_by=request.user,
            modified_by=request.user,
            customer=customer
        )

        # Process captured image from webcam
        if captured_image_data and 'base64' in captured_image_data:
            format, imgstr = captured_image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = base64.b64decode(imgstr)
            file_name = f"receiving_{uuid.uuid4().hex[:10]}.{ext}"

            image_file = InMemoryUploadedFile(
                BytesIO(image_data),
                field_name="receiving_image",
                name=file_name,
                content_type=f"image/{ext}",
                size=len(image_data),
                charset=None
            )
            receiving.receiving_image = image_file

        receiving.save()
        return JsonResponse({
            'print_url': reverse('receiving:print_receiving_slip', args=[receiving.id]),
            'redirect_url': reverse('receiving:add_receiving')
        })

    service_type = ServiceType.objects.all()
    return render(request, 'receiving/add_receiving.html', {
        'service_type': service_type
    })


def print_receiving_slip(request, receiving_id):
    receiving = get_object_or_404(Receiving, pk=receiving_id)
    return render(request, 'receiving/receiving_print_slip.html', {'receiving': receiving})


def search_customers(request):
    query = request.GET.get('q', '')  # Get search query from the request
    customers = Customer.objects.filter(name__icontains=query)  # Filter customers by name
    customer_suggestions = [
        {'name': customer.name, 'phone': customer.phone_number}
        for customer in customers
    ]
    return JsonResponse({'suggestions': customer_suggestions})


def search_receiving(request):
    query = request.GET.get('q', '')  # Get search query from the request
    receivings = Receiving.objects.filter(service_no__contains=query)  # Filter customers by name
    receiving_suggestions = [
        {'service_no': receiving.service_no, 'customer': receiving.customer.name, 'phone': receiving.customer.phone_number}
        for receiving in receivings
    ]
    return JsonResponse({'suggestions': receiving_suggestions})


def receiving_delivery(request):
    return render(request, 'receiving/delivery.html', )

@login_required
def get_receiving(request, service_no):
    try:
        receiving = Receiving.objects.select_related('customer').get(service_no=service_no)

        data = {
            'success': True,
            'receiving': {
                'service_type': receiving.service_type,
                'remarks': receiving.remarks,
                'description': receiving.description,
                'estimated_price': receiving.estimated_price,
                'customer_name': receiving.customer.name,
                'customer_phone': receiving.customer.phone_number,
                'is_delivered': receiving.is_delivered,
                'receiving_image': receiving.receiving_image.url if receiving.receiving_image else None,
            }
        }
    except Receiving.DoesNotExist:
        data = {'success': False}
    return JsonResponse(data)