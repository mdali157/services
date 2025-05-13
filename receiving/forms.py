# receivings/forms.py
from django import forms
from .models import Receiving, ServiceType


class ReceivingForm(forms.ModelForm):
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        empty_label="Select Service Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'})
    )
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = Receiving
        fields = [
            'customer_name',
            'customer_phone',
            'service_type',
            'description',
            'remarks',
        ]