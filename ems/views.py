import imp
from unicodedata import name
from django.shortcuts import render
from event.models import Banner, Event, Status, Image


def index(request, *args, **kwargs):
    eEnd = Status.objects.get(name="Ended")
    eLive = Status.objects.get(name="Live")
    event = Event.objects.filter(status=eEnd)[:10]
    Live = Event.objects.filter(status=eLive)[:4]
    banner = Banner.objects.all()[0]
    img = Image.objects.all()[:10]
    context = {
        'banner': banner,
        'event': event,
        'live': Live,
        'img': img,
    }
    return render(request, "pages/index.html", context)

def terms(request, *args, **kwargs):
    return render(request, "pages/terms.html")

def imageGallary(request, *args, **kwargs):
    status = Status.objects.get(name="Ended")
    event = Event.objects.filter(status=status)[:1]
    if request.method == "POST":
        sku = request.POST.get('sku')
        if sku:
            
            event = Event.objects.get(sku=sku)
    events = Event.objects.all()
    img = Image.objects.filter(event=event)
    context = {
        'img': img,
        'event': event,
        'events': events,
    }
    return render(request, "pages/image-gallary.html", context)

def contact(request, *args, **kwargs):
    return render(request, "pages/contact.html")

def events(request, *args, **kwargs):
    eEnd = Status.objects.get(name="Ended")
    event = Event.objects.filter(status=eEnd)

    context = {
        'events': event,
    }

    return render(request, "pages/events.html", context)

def liveEvents(request, *args, **kwargs):
    eLive = Status.objects.get(name="Live")
    Live = Event.objects.filter(status=eLive)

    context = {
        'events': Live,
    }

    return render(request, "pages/live-events.html", context)