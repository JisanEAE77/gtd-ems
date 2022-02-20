import profile
from typing import Dict, List, Any
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from sympy import false, true, use
from ems.decorator import not_verified, logged_user, guest_user, verified
from account.models import Profile
from password_validator import PasswordValidator
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import re

from account.models import Profile
from event.models import Image

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# Import the client models of the corresponding product module.
from tencentcloud.sms.v20210111 import sms_client, models
# Import the optional configuration classes
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
# Registration Page

@guest_user
def register(request, *args, **kwargs):
    context = {
        "error": [],
    }

    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('uname')
        username = username.lower()
        phone = request.POST.get('phone')
        nationality = request.POST.get('nationality')
        password = request.POST.get('pass')
        email = request.POST.get('email')
        email = email.lower()

        try:
            getUser = User.objects.get(username=username)
            vd = Profile.objects.get(user=getUser)
            if vd.isVerified == "Yes":
                uexists = False
            else:
                uexists = True
        except:
            uexists = True

        try:
            getEmail = User.objects.get(email=email)
            vd = Profile.objects.get(user=getEmail)
            if vd.isVerified == "Yes":
                mexists = False
            else:
                mexists = True
        except:
            mexists = True

        try:
            getPhone = Profile.objects.get(phone=phone)
            if getPhone.isVerified == "Yes":
                pexists = False
            else:
                pexists= True
        except:
            pexists = True

        CEm = checkEmail(email)
        CPs = checkPassword(password)
        CPh = checkPhone(phone)

        if uexists and mexists and pexists and CEm and CPs and CPh and password and fname and lname and nationality and phone:
            print(username, email, password)
            user = User.objects.create_user(first_name=fname, last_name=lname, username=username, email=email, password=password)

            

            if user is not None:
                
                profile = Profile(user=user, phone=phone, nationality=nationality, isVerified="No")
                profile.save()
                user = authenticate(request, username=username, password=password)
                region = 'ch'
                if profile.phone[:4] == "+852":
                    region = "hk"
                if profile.phone[:3] == "+86":
                    region = "ch"
                sendcode(profile.code, region, profile.phone)
                login(request, user)
                return redirect("/verification")
        else:
            if not uexists:
                context["error"].append("Username already exists, please choose another!")
            if not pexists:
                context["error"].append("Phone Number already exists, please choose another!")
            if not CPh:
                context["error"].append("Invalid Phone Number format, enter a valid Phone Number (Internationl Format: +(country code)(rest of the numbers), example: +8613826012321)!")
            if not mexists and CEm:
                context["error"].append("This E-mail is already in use, please try again with another e-mail!")
            if not CEm:
                context["error"].append("Invalid E-mail format, enter a valid E-mail!")
            if not CPs:
                context["error"].append("Weak password! Your password should contain at least one lowercase letter, one uppercase letter, one numeric digit, one special character and must be at least 6 character long!")

    return render(request, "pages/register.html", context)


# Login Page

@guest_user
def userlogin(request, *args, **kwargs):

    context = {
        "error": '',
    }

    if request.method == "POST":
        username = request.POST.get('username')
        username = username.lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect("/")
        else:
            context["error"] = "Invalid login credentials, try again with correct username & password!"

    return render(request, "pages/login.html", context)


# # Username Validator


# def validateusername(request, username):
#     users = User.objects.all()
#     userlist = [user.username for user in users]
#     username = username.lower()

#     if username in userlist:
#         data = {
#             "response": "VALID"
#         }
#         return JsonResponse(data)
#     data = {
#         "response": "INVALID"
#     }
#     return JsonResponse(data)


# # Email Validator


# def validateemail(request, email):
#     users = User.objects.all()
#     emaillist = [user.email for user in users]
#     email = email.lower()

#     if email in emaillist:
#         data = {
#             "response": "VALID"
#         }
#         return JsonResponse(data)
#     data = {
#         "response": "INVALID"
#     }
#     return JsonResponse(data)


# # Login Validator


# def validatelogin(request, username, password):
#     username = username.lower()
#     user = authenticate(username=username, password=password)

#     if user is not None:
#         data = {
#             "response": "VALID"
#         }
#         return JsonResponse(data)

#     data = {
#         "response": "INVALID"
#     }
#     return JsonResponse(data)


# temporary dashboard

@logged_user
def userSettings(request, *args, **kwargs):
    profile = Profile.objects.get(user=request.user)
    context = {
        'phone': profile.phone,
        'error': '',
        'success': '',
        'verified': profile.isVerified,
    }

    if request.method == "POST":
        nPass = request.POST.get('nPass')
        oPass = request.POST.get('oPass')

        if nPass and oPass:
            check = checkPassword(nPass)
            
            user = authenticate(request, username=request.user.username, password=oPass)

            if user is not None:
                if check:
                    user = User.objects.get(username=request.user.username)
                    user.set_password(nPass)
                    user.save()
                    context['success'] = "Password Changed successfully!"
                else:
                    context["error"] = "Weak password! Your password should contain at least one lowercase letter, one uppercase letter, one numeric digit, one special character and must be at least 6 character long!"
            else:
                context['error'] = "Incorrect Old Password!"
            
        else:
            context['error'] = "Fill up both old and new password field!"

    
    return render(request, "pages/settings.html", context)

@logged_user
def collection(request, *args, **kwargs):
    imgs = Image.objects.filter(user=request.user)
    context = {
        "imgs": imgs,
    }
    return render(request, 'pages/collection.html', context)


@logged_user
def changePhone(request, *args, **kwargs):
    profile = Profile.objects.get(user=request.user)
    if profile.isVerified == "Yes":
        return redirect('/settings')

    context = {
        'error': '',
        'success': '',
    }
    
    phone = request.POST.get('phone')
    if checkPhone(phone):
        profile.phone = phone
        profile.save()
    else:
        context['error'] = "Invalid Phone Number format, enter a valid Phone Number (Internationl Format: +(country code)(rest of the numbers), example: +8613826012321)!"
        return redirect('/settings')
    
    context['success'] = 'Phone Number Changed Successfully'

    return redirect('/settings')
# Registration Page

# Email Format Validator


def checkEmail(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False

# Password Strength Check


def checkPassword(password):
    schema = PasswordValidator()
    schema \
        .min(6) \
        .max(100000) \
        .has().uppercase() \
        .has().lowercase() \
        .has().digits() \
        .has().symbols() \
        .has().no().spaces() \

    if schema.validate(password):
        return True
    else:
        return False

def checkPhone(phone):
    try:
        carrier._is_mobile(number_type(phonenumbers.parse(phone)))
        return True
    except:
        return False


@logged_user
def logOut(request):
    logout(request)
    return redirect('/')


@logged_user
@not_verified
def verification(request):
    context = {
        'error': '',
    }
    phone = Profile.objects.get(user=request.user)
    context['phone'] = phone.phone
    if request.method == 'POST':
        code = request.POST.get('code')
       
        if code == str(phone.code):
            phone.isVerified = "Yes"
            phone.save()
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect("/")
        else:
            context['error'] = "Invalid Verification Code, try again!"

    return render(request, 'pages/verification.html', context)


@logged_user
@not_verified
def resend(request):
    profile = Profile.objects.get(user=request.user)
    region = 'ch'
    if profile.phone[:4] == "+852":
        region = "hk"
    if profile.phone[:3] == "+86":
        region = "ch"
    sendcode(profile.code, region, profile.phone)

    return redirect('/verification')


def sendcode(code, region, phoneNumber):
    try:
        # Required steps:
        # Instantiate an authentication object. The Tencent Cloud account key pair `secretId` and `secretKey` need to be passed in as the input parameters.
        # The example here uses the way to read from the environment variable, so you need to set these two values in the environment variable first.
        # You can also write the key pair directly into the code, but be careful not to copy, upload, or share the code to others;
        # otherwise, the key pair may be leaked, causing damage to your properties.
        # Query the CAM key: https://console.cloud.tencent.com/cam/capi
        cred = credential.Credential("AKIDFIH2YrQmOnyvd5uFzrVu3zg7LJ3bH0pO", "UigOr43pLbbNvFK7h17xWpse9PQ9cpre")
        # cred = credential.Credential(
        #     os.environ.get(""),
        #     os.environ.get("")
        # )
        # (Optional) Instantiate an HTTP option
        httpProfile = HttpProfile()
        # If you need to specify the proxy for API access, you can initialize HttpProfile as follows
        # httpProfile = HttpProfile(proxy="http://username:password@proxy IP:proxy port")
        httpProfile.reqMethod = "POST"  # POST request (POST request by default)
        httpProfile.reqTimeout = 30    # Request timeout period in seconds (60 seconds by default)
        httpProfile.endpoint = 'sms.tencentcloudapi.com'  # Specify the access region domain name (nearby access by default)
        # Optional steps:
        # Instantiate a client configuration object. You can specify the timeout period and other configuration items
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # Specify the signature algorithm
        clientProfile.language = "en-US"
        clientProfile.httpProfile = httpProfile
        # Instantiate the client object of the requested product (with SMS as an example)
        # The second parameter is the information on the region you select in Tencent Cloud International. If you select Singapore, you should enter the string `ap-singapore`. Click https://intl.cloud.tencent.com/document/api/382/40466?lang=en#region-list to view the region list.
        client = sms_client.SmsClient(cred, 'ap-guangzhou', clientProfile)
        # Instantiate a request object. You can further set the request parameters according to the API called and actual conditions
        # You can directly check the SDK source code to determine which attributes of `SendSmsRequest` can be set
        # An attribute may be of a basic type or import another data structure
        # We recommend you use the IDE for development where you can easily redirect to and view the documentation of each API and data structure
        req = models.SendSmsRequest()
        # Settings of a basic parameter:
        # The SDK uses the pointer style to specify parameters, so even for basic parameters, you need to use pointers to assign values to them.
        # The SDK provides encapsulation functions for importing the pointers of basic parameters
        # Help link:
        # SMS console: https://console.cloud.tencent.com/smsv2
        # sms helper: https://intl.cloud.tencent.com/document/product/382/3773?from_cn_redirect=1
        # SMS application ID, which is the `SdkAppId` generated after an application is added in the [SMS console], such as 1400006666
        req.SmsSdkAppId = "1400312180"
        # SMS signature content, which should be encoded in UTF-8. You must enter an approved signature, which can be viewed in the [SMS console]
        req.SignName = "椰科技集团"
        # SMS code number extension, which is not activated by default. If you need to activate it, please contact [SMS Helper]
        #   req.ExtendCode = ""
        # User session content, which can carry context information such as user-side ID and will be returned as-is by the server
        #   req.SessionContext = "xxx"
        # `senderid` for Global SMS, which is not activated by default. If you need to activate it, please contact [SMS Helper] for assistance. This parameter should be left empty for Mainland China SMS
        #   req.SenderId = ""
        # Target mobile number in the E.164 standard (+[country/region code][mobile number])
        # Example: +8613711112222, which has a + sign followed by 86 (country/region code) and then by 13711112222 (mobile number). Up to 200 mobile numbers are supported
        req.PhoneNumberSet = [str(phoneNumber)]
        # Template ID. You must enter the ID of an approved template, which can be viewed in the [SMS console]
        if region == "ch":
            req.TemplateId = "1105870"
        elif region == "hk":
            req.TemplateId = "1219223"
        else:
            req.TemplateId = "1105870"
        # Template parameters. If there are no template parameters, leave it empty
        msg = str(code)
        print(msg)
        req.TemplateParamSet = [msg]
            # Initialize the request by calling the `DescribeInstances` method on the client object. Note: the request method name corresponds to the request object
        # The returned `resp` is an instance of the `DescribeInstancesResponse` class which corresponds to the request object
        resp = client.SendSms(req)
        # A string return packet in JSON format is outputted
        print(resp.to_json_string(indent=2))
    except TencentCloudSDKException as err:
        print(err)