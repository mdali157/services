from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import ReceivingForm
from .models import Receiving

@login_required
def add_receivings(request):
    if request.method == 'POST':
        form = ReceivingForm(request.POST, request.FILES)
        if form.is_valid():
            receiving = form.save(commit=False)
            receiving.created_by = request.user
            receiving.modified_by = request.user
            receiving.save()
            return redirect('some_success_page')  # change this to your actual URL name
    else:
        form = ReceivingForm()
    
    return render(request, 'receiving/add_receiving.html', {'form': form})