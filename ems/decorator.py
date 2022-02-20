from django.shortcuts import redirect
from account.models import Profile

def logged_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/login?next=' + str(request.path))
    return wrapper_func

def verified(view_func):
    def wrapper_func(request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        if profile.isVerified == "Yes":
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/verification?next=' + str(request.path))
    return wrapper_func

def not_verified(view_func):
    def wrapper_func(request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        if profile.isVerified == "No":
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper_func

def guest_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper_func