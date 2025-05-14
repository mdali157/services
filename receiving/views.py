import base64
import uuid
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import *
from customers.models import Customer


# @login_required
# def add_receivings(request):
#     if request.method == 'POST':
#         service_type = request.POST.get("service_type")
#         customer_name = request.POST.get("customer_name")
#         customer_phone = request.POST.get("customer_phone")
#         remarks = request.POST.get("remarks")
#         description = request.POST.get("description")
#         estimated_price = request.POST.get("estimated_price")
#         # form = ReceivingForm()
#     service_type = ServiceType.objects.all()
#     return render(request, 'receiving/add_receiving.html', {'service_type': service_type})


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
