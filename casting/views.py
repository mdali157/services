import base64
import uuid
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from customers.models import Customer

from .models import *


# Create your views here.
@login_required
def add_casting(request):
    if request.method == 'POST':
        # 1. Read form fields
        customer_name = request.POST.get("customer_name", "").strip().capitalize()
        customer_phone = request.POST.get("customer_phone", "").strip()
        karate_value = request.POST.get("karate", "").strip().capitalize()
        color_value = request.POST.get("color", "").strip().capitalize()
        description = request.POST.get("description", "").strip()
        creation_date = request.POST.get("creation_date")  # YYYY-MM-DD
        captured_image_data = request.POST.get("captured_image")  # data:image/png;base64,....

        # 2. Get or create customer
        customer, created = Customer.objects.get_or_create(
            name=customer_name,
            phone_number=customer_phone,
            defaults={'added_by': request.user}
        )

        karate, created = Karate.objects.get_or_create(
            name=karate_value
        )

        color, created = Color.objects.get_or_create(
            name=color_value
        )

        # 3. Build Casting instance
        casting = Casting(
            customer=customer,
            karate=karate.name,
            color=color.name,
            description=description,
            created_at=creation_date,
            created_by=request.user,
            modified_by=request.user,
        )

        # 4. Handle base64 image
        if captured_image_data and ';base64,' in captured_image_data:
            header, b64data = captured_image_data.split(';base64,')
            ext = header.split('/')[-1]  # e.g. "png" or "jpeg"
            binary = base64.b64decode(b64data)
            fname = f"casting_{uuid.uuid4().hex[:10]}.{ext}"
            img_file = InMemoryUploadedFile(
                BytesIO(binary),
                field_name='image',
                name=fname,
                content_type=f"image/{ext}",
                size=len(binary),
                charset=None
            )
            casting.image = img_file

        # 5. Save (casting_no auto-assigned in model.save())
        casting.save()

        # 6. Respond with JSON for your AJAX
        return JsonResponse({
            'print_url': reverse('casting:print_casting_slip', args=[casting.id]),
            'redirect_url': reverse('casting:add_casting')
        })

    # GET: figure next casting_no and render
    max_no = Casting.objects.aggregate(max=Max('casting_no'))['max']
    next_no = 111111 if max_no is None else max_no + 1

    return render(request, 'casting/add_casting.html', {
        'next_casting_no': next_no
    })


def search_karate(request):
    query = request.GET.get('q', '')
    all_karate = Karate.objects.filter(name__icontains=query)
    karate_suggestions = [
        {'name': karate.name}
        for karate in all_karate
    ]
    return JsonResponse({'suggestions': karate_suggestions})


def search_casting(request):
    query = request.GET.get('q', '')
    all_colors = Color.objects.filter(name__icontains=query)
    color_suggestions = [
        {'name': color.name}
        for color in all_colors
    ]
    return JsonResponse({'suggestions': color_suggestions})


def print_casting_slip(request, casting_id):
    casting = get_object_or_404(Casting, pk=casting_id)
    return render(request, 'casting/casting_print_slip.html', {'casting': casting})

def all_flask(request):
    flasks = Flask.objects.all().order_by('-created_at')
    return render(request, 'casting/all_flask.html', {
        'all_flask': flasks,
    })

@login_required
def add_flask(request):
    next_id = (Flask.objects.aggregate(Max('id'))['id__max'] or 0) + 1
    unflasked = Casting.objects.filter(flask__isnull=True)

    if request.method == 'POST':
        # 1. Create Flask
        flask = Flask.objects.create(
            karate=request.POST.get("karate", "").strip(),
            color=request.POST.get("color", "").strip(),
            input_weight=request.POST.get("input_weight", ""),
            output_weight=request.POST.get("output_weight", ""),
            machine_wastage=request.POST.get("machine_wastage", ""),
            production_weight=request.POST.get("production_weight", ""),
            created_at=request.POST.get("creation_date", ""),
        )

        # 2. Loop through selected castings and update each
        for key in request.POST:
            if key.startswith("casting_") and key.endswith("_weight"):
                base = key.replace("_weight", "")  # casting_12
                casting_sno = base.split("_")[1]
                try:
                    casting = Casting.objects.get(id=casting_sno)
                except Casting.DoesNotExist:
                    continue

                # Update casting fields
                casting.weight = request.POST.get(f"{base}_weight")
                casting.converted24k = request.POST.get(f"{base}_converted")
                casting.wastage_percentage = request.POST.get(f"{base}_wastage_percent")
                casting.wastage_weight = request.POST.get(f"{base}_wastage_weight")
                casting.total_weight24k = request.POST.get(f"{base}_total_24k")
                casting.gold_received = request.POST.get(f"{base}_gold_received")
                casting.service_charges_rate = request.POST.get(f"{base}_service_rate")
                casting.service_charges_amount = request.POST.get(f"{base}_service_amount")
                casting.cash_received = request.POST.get(f"{base}_cash_received")
                casting.flask = flask
                casting.modified_by = request.user
                casting.save()

        return redirect('casting:all_flask')

    return render(request, 'casting/add_flask.html', {
        'next_flask_id': next_id,
        'unflasked_castings': unflasked,
    })