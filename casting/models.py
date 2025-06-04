from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from customers.models import Customer


# Create your models here.
class Flask(models.Model):
    karate = models.CharField(max_length=158 ,blank=True, null=True)
    color = models.CharField(max_length=158 ,blank=True, null=True)
    input_weight = models.CharField(max_length=158 ,blank=True, null=True)
    output_weight = models.CharField(max_length=158 ,blank=True, null=True)
    machine_wastage = models.CharField(max_length=158 ,blank=True, null=True)
    production_weight = models.CharField(max_length=158 ,blank=True, null=True)
    created_at = models.DateField(default=now, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)



class Color(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Karate(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Casting(models.Model):
    karate = models.CharField(max_length=158 ,blank=True, null=True)
    color = models.CharField(max_length=158 ,blank=True, null=True)
    casting_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    delivery_image = models.ImageField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    flask = models.ForeignKey(Flask, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.CharField(max_length=158 ,blank=True, null=True)
    converted24k = models.CharField(max_length=158 ,blank=True, null=True)
    wastage_percentage = models.CharField(max_length=158 ,blank=True, null=True)
    wastage_weight = models.CharField(max_length=158 ,blank=True, null=True)
    total_weight24k = models.CharField(max_length=158 ,blank=True, null=True)
    gold_received = models.CharField(max_length=158 ,blank=True, null=True)
    service_charges_rate = models.CharField(max_length=158 ,blank=True, null=True)
    service_charges_amount = models.CharField(max_length=158 ,blank=True, null=True)
    cash_received = models.CharField(max_length=158 ,blank=True, null=True)
    remarks = models.CharField(max_length=158 ,blank=True, null=True)
    created_at = models.DateField(default=now, blank=True, null=True)
    is_delivered = models.BooleanField(default=False, null=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_casting')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_casting')

    def save(self, *args, **kwargs):
        if self.casting_no is None:
            last = Casting.objects.order_by('-casting_no').first()
            self.casting_no = 111111 if not last or not last.casting_no else last.casting_no + 1
        super().save(*args, **kwargs)

    def __str__(self):
        # Check if casting_no or customer.name is None, and provide a default value
        casting_no_str = str(self.casting_no) if self.casting_no else 'No Casting No'
        customer_name = self.customer.name if self.customer else 'No Customer'
        return f"{casting_no_str} {customer_name} {self.description or 'No Description'}"
