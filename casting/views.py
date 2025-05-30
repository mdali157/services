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


@login_required
def update_casting(request, casting_id):
    casting = get_object_or_404(Casting, pk=casting_id)

    if request.method == 'POST':
        # 1. Read form fields
        karate_value = request.POST.get("karate", "").strip().capitalize()
        color_value = request.POST.get("color", "").strip().capitalize()
        description = request.POST.get("description", "").strip()
        delivery_remarks = request.POST.get("delivery_remarks", "").strip()
        creation_date = request.POST.get("creation_date")  # YYYY-MM-DD
        captured_image_data = request.POST.get("captured_image")  # data:image/png;base64,…
        is_delivered = request.POST.get('is_delivered')


        karate_obj, _ = Karate.objects.get_or_create(name=karate_value)
        color_obj, _ = Color.objects.get_or_create(name=color_value)

        # 3. Update fields on casting
        casting.karate = karate_obj.name
        casting.color = color_obj.name
        casting.description = description
        casting.remarks = delivery_remarks
        casting.created_at = creation_date
        casting.is_delivered = is_delivered == 'on'
        casting.modified_by = request.user

        # 4. Handle new base64 image if provided
        if captured_image_data and ';base64,' in captured_image_data:
            header, b64data = captured_image_data.split(';base64,')
            ext = header.split('/')[-1]
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
            casting.delivery_image = img_file

        casting.save()
        return redirect('casting:all_casting')

    return render(request, 'casting/update_casting.html', {
        'casting': casting
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


def casting_flask_print_slip(request, casting_id):
    casting = get_object_or_404(Casting, pk=casting_id)
    return render(request, 'casting/casting_flask_print_slip.html', {'casting': casting})


def all_flask(request):
    flasks = Flask.objects.all().order_by('-created_at')
    return render(request, 'casting/all_flask.html', {
        'all_flask': flasks,
    })


def all_casting(request):
    status = request.GET.get('status', 'undelivered')

    if status == 'delivered':
        all_casting = Casting.objects.filter(is_delivered=True)
    elif status == 'undelivered':
        all_casting = Casting.objects.filter(is_delivered=False)
    else:  # 'all'
        all_casting = Casting.objects.all()



    return render(request, 'casting/all_casting.html', {
        'castings_with_flask': all_casting,
        'selected_status': status,
    })


@login_required
def add_flask(request):
    # 1. Determine next_flask_id (just max ID + 1)
    next_id = (Flask.objects.aggregate(Max('id'))['id__max'] or 0) + 1

    # 2. Fetch all castings not yet assigned to a flask
    unflasked = Casting.objects.filter(flask__isnull=True)

    if request.method == 'POST':
        # 3. Extract and normalize karate & color strings
        karate_value = request.POST.get("karate", "").strip().capitalize()
        color_value = request.POST.get("color", "").strip().capitalize()

        # 4. Get or create the Karate and Color objects
        karate_obj, _ = Karate.objects.get_or_create(name=karate_value)
        color_obj, _ = Color.objects.get_or_create(name=color_value)

        # 5. Create the Flask instance (saving karate_obj.name & color_obj.name, to mirror how Casting saved them)
        flask = Flask.objects.create(
            karate=karate_obj.name,
            color=color_obj.name,
            input_weight=request.POST.get("input_weight", ""),
            output_weight=request.POST.get("output_weight", ""),
            machine_wastage=request.POST.get("machine_wastage", ""),
            production_weight=request.POST.get("production_weight", ""),
            created_at=request.POST.get("creation_date", ""),
            # If your Flask model instead has FK fields for karate & color:
            # karate=karate_obj,
            # color=color_obj,
        )

        # 6. Loop through POST keys to find all selected castings (those ending with "_sno")
        for key in request.POST:
            if key.startswith("casting_") and key.endswith("_sno"):
                base = key.replace("_sno", "")  # e.g. "casting_12"
                casting_id = base.split("_")[1]
                try:
                    casting = Casting.objects.get(id=casting_id)
                except Casting.DoesNotExist:
                    continue

                # 7. Update each Casting’s fields
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

        # 8. Redirect back to the “all_flask” page
        return redirect('casting:all_flask')

    # For GET requests, render the form with next_flask_id & unflasked_castings
    return render(request, 'casting/add_flask.html', {
        'next_flask_id': next_id,
        'unflasked_castings': unflasked,
    })


@login_required
def update_flask(request, flask_id):
    flask = get_object_or_404(Flask, id=flask_id)

    # 1. All castings already linked to this flask
    existing_castings = Casting.objects.filter(flask=flask)

    # 2. Castings not yet linked to any flask (for the “Add New Castings” select)
    unlinked_castings = Casting.objects.filter(flask__isnull=True)

    if request.method == 'POST':
        # a) Normalize & get_or_create Karate and Color
        karate_value = request.POST.get("karate", "").strip().capitalize()
        color_value = request.POST.get("color", "").strip().capitalize()

        karate_obj, _ = Karate.objects.get_or_create(name=karate_value)
        color_obj,  _ = Color.objects.get_or_create(name=color_value)

        # b) Update Flask fields
        flask.karate = karate_obj.name
        flask.color = color_obj.name
        flask.input_weight = request.POST.get("input_weight", "")
        flask.output_weight = request.POST.get("output_weight", "")
        flask.machine_wastage = request.POST.get("machine_wastage", "")
        flask.production_weight = request.POST.get("production_weight", "")
        flask.created_at = request.POST.get("creation_date", "")
        flask.save()

        # c) Update data for castings already linked
        for casting in existing_castings:
            prefix = f"casting_{casting.id}_"
            casting.weight = request.POST.get(f"{prefix}weight")
            casting.converted24k = request.POST.get(f"{prefix}converted")
            casting.wastage_percentage = request.POST.get(f"{prefix}wastage_percent")
            casting.wastage_weight = request.POST.get(f"{prefix}wastage_weight")
            casting.total_weight24k = request.POST.get(f"{prefix}total_24k")
            casting.gold_received = request.POST.get(f"{prefix}gold_received")
            casting.service_charges_rate = request.POST.get(f"{prefix}service_rate")
            casting.service_charges_amount = request.POST.get(f"{prefix}service_amount")
            casting.cash_received = request.POST.get(f"{prefix}cash_received")
            casting.modified_by = request.user
            casting.save()

        # d) Link & initialize data for any newly selected castings
        selected_ids = request.POST.getlist("related_castings")
        for casting_id in selected_ids:
            # Only link if it wasn't already linked
            if not existing_castings.filter(id=casting_id).exists():
                casting = get_object_or_404(Casting, id=casting_id)
                prefix = f"casting_{casting.id}_"
                casting.weight = request.POST.get(f"{prefix}weight")
                casting.converted24k = request.POST.get(f"{prefix}converted")
                casting.wastage_percentage = request.POST.get(f"{prefix}wastage_percent")
                casting.wastage_weight = request.POST.get(f"{prefix}wastage_weight")
                casting.total_weight24k = request.POST.get(f"{prefix}total_24k")
                casting.gold_received = request.POST.get(f"{prefix}gold_received")
                casting.service_charges_rate = request.POST.get(f"{prefix}service_rate")
                casting.service_charges_amount = request.POST.get(f"{prefix}service_amount")
                casting.cash_received = request.POST.get(f"{prefix}cash_received")
                casting.flask = flask
                casting.modified_by = request.user
                casting.save()

        return redirect('casting:all_flask')

    # GET → render template with context
    return render(request, 'casting/update_flask.html', {
        'flask': flask,
        'existing_castings': existing_castings,
        'unlinked_castings': unlinked_castings,
    })
