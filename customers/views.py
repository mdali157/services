from django.http import JsonResponse
from .models import Customer

def search_customers(request):
    query = request.GET.get('q', '')  # Get search query from the request
    customers = Customer.objects.filter(customer_name__icontains=query)  # Filter customers by name
    customer_suggestions = [
        {'name': customer.customer_name, 'phone': customer.phone_number}
        for customer in customers
    ]
    return JsonResponse({'suggestions': customer_suggestions})
