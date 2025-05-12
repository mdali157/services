# receivings/forms.py
from django import forms
from .models import Receiving, ServiceType

class ReceivingForm(forms.ModelForm):
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        empty_label="Select Service Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Receiving
        fields = [
            'service_type',
            'description',
            'remarks',
            'estimated_price',
            'actual_price',
            'receiving_image',
            'delivery_image'
        ]
