import base64
import datetime
import io
import uuid
from io import BytesIO

import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.urls import reverse
from openpyxl.utils import get_column_letter
from xhtml2pdf import pisa

from customers.models import Customer
from receiving.models import ServiceType, Receiving

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
        color_obj, _ = Color.objects.get_or_create(name=color_value)

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



def report(request):
    """
    Handles both GET (render the filter form) and POST (generate PDF inline or
    Excel download).
    """
    service_type_list = ServiceType.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        # 1) Read form fields
        report_for = request.POST.get("report_for")           # "Services" or "Casting"
        from_date_str = request.POST.get("from_date")         # e.g. "2025-05-01"
        to_date_str = request.POST.get("to_date")             # e.g. "2025-05-31"
        report_type = request.POST.get("report_type")         # "Summary" or "Detail"
        selected_customers = request.POST.getlist("customers")  # list of customer IDs (strings)
        selected_service_type = request.POST.get("service_type")  # e.g. "Gold Plating" or "All"
        action = request.POST.get("action")                   # "pdf" or "excel"

        # 2) Parse dates into date objects
        #    (Use .strptime to get naive dates, then attach UTC or local if needed)
        from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.datetime.strptime(to_date_str, "%Y-%m-%d").date()

        # 3) Build queryset depending on `report_for`
        if report_for == "Services":
            qs = Receiving.objects.filter(created_at__range=(from_date, to_date))
            if selected_customers:
                qs = qs.filter(customer__id__in=selected_customers)
            if selected_service_type and selected_service_type != "All":
                qs = qs.filter(service_type=selected_service_type)

        else:  # report_for == "Casting"
            qs = Casting.objects.filter(created_at__range=(from_date, to_date))
            if selected_customers:
                qs = qs.filter(customer__id__in=selected_customers)

        # 4) Branch on action
        if action == "pdf":
            return generate_pdf_response(
                request=request,
                queryset=qs,
                report_for=report_for,
                report_type=report_type,
                from_date=from_date,
                to_date=to_date,
            )
        else:  # action == "excel"
            return generate_excel_response(
                queryset=qs,
                report_for=report_for,
                report_type=report_type,
                from_date=from_date,
                to_date=to_date,
            )

    # If GET, just render the filter form
    return render(
        request,
        "casting/reports.html",
        {"service_type": service_type_list, "customers": customers},
    )


def generate_pdf_response(request, queryset, report_for, report_type, from_date, to_date):
    """
    Renders the `report_pdf.html` template into a PDF (xhtml2pdf) and returns
    it inline (Content-Disposition: inline).
    """
    # 1) Build context for the PDF template
    context = {
        "report_for": report_for,
        "report_type": report_type,
        "from_date": from_date,
        "to_date": to_date,
        "items": queryset,  # Receivings or Castings
    }

    # 2) Load and render the HTML template
    template = get_template("casting/report_pdf.html")
    html = template.render(context)

    # 3) Create a bytes buffer, write PDF into it
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    # 4) Return the PDF with inline disposition
    result.seek(0)
    response = HttpResponse(result.read(), content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="report.pdf"'
    return response


def generate_excel_response(queryset, report_for, report_type, from_date, to_date):
    """
    Builds an openpyxl Workbook in-memory, writes headers + rows depending on
    `report_for` and `report_type`, and returns an HttpResponse that forces
    download (Content-Disposition: attachment).
    """
    wb = openpyxl.Workbook()
    ws = wb.active

    # 1) Build column headers depending on report_for and report_type
    if report_for == "Services":
        if report_type == "Detail":
            headers = [
                "Service #",
                "Date",
                "Type",
                "Customer Name",
                "Mobile #",
                "Work Description",
                "Estimate",
                "Amount",
                "Remarks",
            ]
        else:  # Summary
            headers = ["Date", "Type", "Estimate", "Amount"]
    else:  # report_for == "Casting"
        if report_type == "Detail":
            headers = [
                "Flask #", "Date", "Karate", "Color", "Input WT", "Output WT", "Machine Wastage",
                "Cast #", "Party Name", "Production Weight", "Weight-24K", "Wastage %",
                "Wastage Wt", "Total Wt", "Gold Received", "Service Charges Rate", "Amount",
                "Received Amount", "Remarks"
            ]

        else:  # Summary
            headers = [
                "Date",
                "Input WT",
                "Output WT",
                "Machine Wastage",
                "Production Weight",
                "Weight-24K",
                "Wastage Wt",
                "Total Wt",
                "Gold Received",
                "Service Amount",
                "Received Amount",
            ]

    # 2) Write the header row
    for col_idx, column_title in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = column_title
        # (Optional) enlarge column width a bit:
        ws.column_dimensions[get_column_letter(col_idx)].width = max(len(column_title) * 1.2, 15)

    # 3) Write each row
    row_num = 2
    for obj in queryset:
        row = []
        if report_for == "Services":
            if report_type == "Detail":
                row = [
                    obj.service_no,
                    obj.created_at.strftime("%Y-%m-%d"),
                    obj.service_type,
                    obj.customer.name,
                    obj.customer.phone_number,
                    obj.description,
                    obj.estimated_price or "",
                    obj.actual_price or "",
                    obj.remarks or "",
                ]
            else:  # Summary
                row = [
                    obj.created_at.strftime("%Y-%m-%d"),
                    obj.service_type,
                    obj.estimated_price or "",
                    obj.actual_price or "",
                ]
        else:  # report_for == "Casting"
            if report_type == "Detail":
                row = [
                    obj.flask.id if obj.flask else "",
                    obj.created_at.strftime("%Y-%m-%d"),
                    obj.karate or "",
                    obj.color or "",
                    obj.flask.input_weight if obj.flask else "",
                    obj.flask.output_weight if obj.flask else "",
                    obj.flask.machine_wastage if obj.flask else "",
                    obj.casting_no,
                    obj.customer.name if obj.customer.name else "",
                    obj.flask.production_weight if obj.flask else "",
                    obj.total_weight24k or "",
                    obj.wastage_percentage or "",
                    obj.wastage_weight or "",
                    obj.total_weight24k or "",
                    obj.gold_received or "",
                    obj.service_charges_rate or "",
                    obj.service_charges_amount or "",
                    obj.cash_received or "",
                    obj.remarks if obj.remarks else "",
                ]

            else:  # Summary
                row = [
                    obj.created_at.strftime("%Y-%m-%d"),
                    obj.flask.input_weight if obj.flask else "",
                    obj.flask.output_weight if obj.flask else "",
                    obj.flask.machine_wastage if obj.flask else "",
                    obj.flask.production_weight if obj.flask else "",
                    obj.total_weight24k or "",
                    obj.wastage_weight or "",
                    obj.total_weight24k or "",
                    obj.gold_received or "",
                    obj.service_charges_amount or "",
                    obj.cash_received or "",
                ]

        for col_idx, cell_value in enumerate(row, 1):
            ws.cell(row=row_num, column=col_idx).value = cell_value

        row_num += 1

    # 4) Stream the workbook to an in-memory buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"{report_for.lower()}_{report_type.lower()}_{from_date}_{to_date}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response