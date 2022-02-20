from django.shortcuts import render, redirect
from event.models import Event, Image, Tag
from django.db.models import Count
from ems.decorator import logged_user, verified
import qrcode
from PIL import Image as IMG

# Create your views here.

def singleEvent(request, uid):
    event = Event.objects.get(sku=uid)
    # imgs = Image.objects.filter(event=event)
    imgs = Image.objects.annotate(v_count=Count('votes')).order_by('-v_count', 'user')
    context = {
        'event': event,
        'imgs': imgs,
    }

    return render(request, 'pages/single-event.html', context)

@logged_user
@verified
def upload(request, uid):
    event = Event.objects.get(sku=uid)
    context = {
        'event': event,
        'error': '',
        'title': '',
        'desc': '',
    }
    if request.method == "POST":
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        img = request.FILES.get('img')
        tag = request.POST.get('tag')

        context['title'] = title
        context['desc'] = desc

        if tag and title and desc and img:
            
            tag = Tag.objects.get(name=tag)
            total = Image.objects.filter(user=request.user, tag = tag)

            
            
            if tag in event.tags.all():
                if total.count() <= event.limit:
                    image = Image(user=request.user, event=event, tag=tag, image=img, title=title, desc=desc)
                    image.save()

                    return redirect("/image/" + str(image.sku))
                else:
                    context['error'] = "You have uploaded the maximum amount (" + str(event.limit + 1) + ") of image for this tag"
            else:
                context['error'] = "Select a tag for your image."
        else:
            context['error'] = "Please fill up all the required field to upload your photo!"
    
    

    return render(request, 'pages/upload.html', context)

def gallary(request, uid):
    e = Event.objects.get(sku=uid)
    imgs = Image.objects.annotate(v_count=Count('votes')).order_by('-v_count', 'user')
    images = imgs.filter(event=e)
    context = {
        'images': images,
        'events': e,
    }
    return render(request, 'pages/event-gallary.html', context)


def image(request, uid):
    img = Image.objects.get(sku=uid)
    check = False
    check2 = False

    if request.user in img.votes.all():
        check = True

    if request.user.username == img.user.username and img.event.status.name == "Live":
        check2 = True

    context = {
        'img': img,
        'voted': check,
        'withdraw': check2,
    }

    return render(request, 'pages/single-image.html', context)

@logged_user
@verified
def vote(request, uid):
    img = Image.objects.get(sku=uid)
    img.votes.add(request.user)
    img.save()

    return redirect('/image/'+str(uid))

@logged_user
@verified
def unvote(request, uid):
    img = Image.objects.get(sku=uid)
    img.votes.remove(request.user)
    img.save()

    return redirect('/image/'+str(uid))

@logged_user
@verified
def delete(request, uid):
    img = Image.objects.get(sku=uid)
    if img.event.status.name == "Live":
        esku = img.event.sku
        img.delete()
    else:
        return redirect('/image/'+str(img.sku))

    return redirect('/gallary/'+str(esku))


# def QRCode(event, code):
#     e = Event.objects.get(sku=code)
#     cover = e.image
#     current_site = Site.objects.get_current()
#     current_site.domain
#     link = str(current_site.domain) + "/" + event + "/" + code
#     img = qrcode.make(link)
#     # img.save("../media/" + event + "QR/" + code + ".jpg")
#     bg_w, bg_h = cover.size
#     img_w, img_h = img.size
#     offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
#     cover.paste(img, offset)
#     cover.save("../media/" + event + "QR/" + code + ".jpg")
