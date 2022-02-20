from distutils.core import run_setup
from pyexpat import model
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
import uuid

from random import randint

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    nationality = models.CharField(max_length=50)
    code = models.CharField(default=random_with_N_digits(6), max_length=10)
    isVerified = models.CharField(max_length=10)

    def __str__(self):
        return str(self.user)