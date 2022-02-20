"""ems URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from unicodedata import name
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import index, terms, imageGallary, contact, events, liveEvents
from account.views import register, userlogin, logOut, verification, resend, userSettings, collection, changePhone
from event.views import singleEvent, upload, gallary, image, vote, delete, unvote

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('event/<str:uid>', singleEvent, name="event-details"),
    path('upload/<str:uid>', upload, name="upload"),
    path('gallary/<str:uid>', gallary, name="gallary"),
    path('image/<str:uid>', image, name="single-image"),
    path('vote/<str:uid>', vote, name="vote"),
    path('delete/<str:uid>', delete, name="delete"),
    path('register', register, name="register"),
    path('login', userlogin, name="login"),
    path('unvote/<str:uid>', unvote, name="unvote"),
    path('logout', logOut, name="logout"),
    path('verification', verification, name="verification"),
    path('terms', terms, name="terms"),
    path('image-gallary', imageGallary, name="events"),
    path('contact', contact, name="contact"),
    path('resend', resend, name="resend"),
    path('settings', userSettings, name="settings"),
    path('my-collection', collection, name="collection"),
    path('events', events, name="events"),
    path('live-events', liveEvents, name="live-events"),
    path('changePhone', changePhone, name="changePhone")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)