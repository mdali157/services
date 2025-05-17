from django.http import JsonResponse
from django.shortcuts import render

from customers.models import Customer


# Create your views here.

def search_customers(request):
    query = request.GET.get('q', '')  # Get search query from the request
    customers = Customer.objects.filter(name__icontains=query)  # Filter customers by name
    customer_suggestions = [
        {'name': customer.name, 'phone': customer.phone_number}
        for customer in customers
    ]
    return JsonResponse({'suggestions': customer_suggestions})
