from unittest.mock import DEFAULT

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from customers.models import Customer
# Create your models here.

class ServiceType(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Receiving(models.Model):
    service_type = models.CharField(max_length=255,  blank=True, null=True)
    service_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=255)
    remarks = models.CharField(max_length=158 ,blank=True, null=True)
    delivery_remarks = models.CharField(max_length=158 ,blank=True, null=True)
    estimated_price = models.IntegerField(blank=True, null=True)
    actual_price = models.IntegerField(blank=True, null=True)
    receiving_image = models.ImageField(blank=True, null=True)
    delivery_image = models.ImageField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False, null=False)
    created_at = models.DateField(default=now, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_receivings')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_receivings')

    def save(self, *args, **kwargs):
        if self.service_no is None:
            last = Receiving.objects.order_by('-service_no').first()
            self.service_no = 111111 if not last or not last.service_no else last.service_no + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.service_no) + ' ' + self.customer.name + ' ' + self.description