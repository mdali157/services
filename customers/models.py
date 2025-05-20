from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15,  blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + " - " + self.phone_number
