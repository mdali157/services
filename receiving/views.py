from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReceivingForm
from .models import Receiving, Customer
from django.views.generic.edit import CreateView
from django.http import JsonResponse

@login_required
def add_receivings(request):
    if request.method == 'POST':
        form = ReceivingForm(request.POST, request.FILES)
        if form.is_valid():
            receiving = form.save(commit=False)
            description = form.cleaned_data.get('description', '')
            receiving.estimated_price = int(len(description) * 0.5)  # Convert to int if needed
            receiving.created_by = request.user
            receiving.modified_by = request.user
            receiving.save()
            print("Data Saved Successfully") # For Debugging
            return redirect('home')
    else:
        form = ReceivingForm()
    return render(request, 'receiving/add_receiving.html', {'form': form})


@login_required
def customer_autocomplete(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(name__icontains=query)[:10]
    results = [{'name': c.name, 'phone': c.phone} for c in customers]
    return JsonResponse(results, safe=False)