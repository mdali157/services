from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from customers.models import Customer


# Create your models here.
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
    description = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True)
    delivery_image = models.ImageField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateField(default=now, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_casting')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modified_casting')

    def save(self, *args, **kwargs):
        if self.casting_no is None:
            last = Casting.objects.order_by('-casting_no').first()
            self.service_no = 111111 if not last or not last.casting_no else last.casting_no + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.casting_no) + ' ' + self.customer.name + ' ' + self.description