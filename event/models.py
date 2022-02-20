from datetime import datetime
from operator import mod
from pyexpat import model
from django.db import models
import uuid
from django.contrib.auth.models import User
import os
from pathlib import Path
from PIL import Image as IMG
import qrcode
from django.contrib.sites.models import Site
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

# Create your models here.
class Domain(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Banner(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(blank=False, null=False, upload_to="banners/")
    title = models.CharField(max_length=300)
    short_desc = models.TextField(max_length=800)
    endTime = models.DateTimeField(default=datetime.now)
    link = models.CharField(max_length=300)


    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=300)
    desc = models.TextField(max_length=3000)
    endTime = models.DateTimeField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    image = models.ImageField(blank=False, null=False, upload_to="events/")
    sku = models.UUIDField(max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False)
    tags = models.ManyToManyField(Tag)
    limit = models.IntegerField(default=0)

   
    def save(self, *args, **kwargs):
        if not self.pk:
            dirname = os.path.join(BASE_DIR, 'media')
            os.mkdir(os.path.join(dirname, str(self.sku)))
            cover = IMG.open(self.image)
            current_site = Site.objects.all()[:1]
            link = str(current_site[0].domain) + "/event/" + str(self.sku)
            img = qrcode.make(link)
            bg_w, bg_h = cover.size
            img_w, img_h = img.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            cover.paste(img, offset)
            cover.save(dirname + "/eventQR/" + str(self.sku) + ".jpg")
        super().save(*args, **kwargs)  # Call the "real" save() method.      

    def __str__(self):
        return str(self.sku)

class Image(models.Model):
    def folder_name(self, filename):
        now = datetime.now()

        current_time = now.strftime("%d-%m-%Y %H-%M-%S")
        return str(self.event.sku) + '/' + str(self.user.username) + '-' + str(self.tag.name) + '---' + str(current_time) + ".jpg"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    image = models.ImageField(blank=False, null=False, upload_to=folder_name)
    sku = models.UUIDField(max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    desc = models.TextField(max_length=1000)
    votes = models.ManyToManyField(User, related_name="votes", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            dirname = os.path.join(BASE_DIR, 'media')
            cover = IMG.open(self.image)
            current_site = Site.objects.all()[:1]
            link = str(current_site[0].domain) + "/image/" + str(self.sku)
            img = qrcode.make(link)
            bg_w, bg_h = cover.size
            img_w, img_h = img.size
            offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
            cover.paste(img, offset)
            cover.save(dirname + "/imageQR/" + str(self.sku) + ".jpg")
        super().save(*args, **kwargs)  # Call the "real" save() method. 

    def __str__(self):
        return str(self.image)
