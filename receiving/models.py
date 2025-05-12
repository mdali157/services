from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class ServiceType(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name  # This will ensure the name of the service type is displayed (e.g., Soldering, Engraving)

class Receiving(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True)
    service_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=255)
    remarks = models.CharField(max_length=158)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_receivings')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_receivings')

    def save(self, *args, **kwargs):
        if self.service_no is None:
            last = Receiving.objects.order_by('-service_no').first()
            self.service_no = 111111 if not last or not last.service_no else last.service_no + 1
        super().save(*args, **kwargs)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
