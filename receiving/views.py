from django.shortcuts import render


# Create your views here.
def add_receivings(request):
    context = {}
    return render(request, 'eggs/eggs_record_details.html', context)
