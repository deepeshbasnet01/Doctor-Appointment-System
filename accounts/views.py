from unittest import FunctionTestCase
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse,redirect
from accounts.decorators import only_non_authorized
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm
from .models import User, WeekDayAvailable
from django.contrib import messages, auth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from django.utils.encoding import force_bytes


@only_non_authorized
def register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            user.is_patient=True 
            user.username = user.email
            user.save()
            messages.success(request, f'{str(user)} was successfully registerd !')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    context = {'form':form,}
    return render(request,'accounts/patient-register.html',context)



@only_non_authorized
def login(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        remember_me=request.POST.get('remember_me')
        print('you must remember ',remember_me)
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            if not remember_me:
                request.session.set_expiry(0) 
            if user.is_staff:
                return redirect("/admin")
            if user.is_patient:
                return redirect('Management_system:patientdashboard')
            if user.is_doctor:
                return redirect('doctor:doctor-dashboard')

        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'accounts/Login.html')
    return render(request, 'accounts/Login.html')



def logout(request):
    auth.logout(request)
    return redirect('accounts:login')

weekday =["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]



@only_non_authorized
def doctor_register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        license_number = request.POST.get("license_number")
        if form.is_valid():
            user =form.save(commit=False)
            user.is_doctor=True 
            user.license_number=license_number
            user.username = user.email
            if len(license_number) != 10 or not license_number.startswith("NP"):
                messages.error(request, 'Please Enter Valid License Data!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if User.objects.filter(license_number = license_number).exists():
                messages.error(request, 'Doctor with this license data already registered !')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            user.save()
            for i in weekday:
                WeekDayAvailable.objects.create(name=i,user=user)
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    context = {'form':form,}
    return render(request, 'accounts/doctor-register.html',context)

@only_non_authorized
def forget_password(request):
    if request.method=="POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        print('user is ',user)
        if not user:
            messages.error(request, 'No User Found With This Email !')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        domain = request.META['HTTP_HOST']
        email_data ={
                "email":user.email,
                'domain':domain,
                'site_name': 'Perfect Strata Maintenance',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
        message = render_to_string('accounts/password_reset_email.html', email_data)
        email = EmailMessage(
                "Reset Your Password",
                message,
                settings.EMAIL_HOST_USER,
                to = [user.email]
                )
        email.content_subtype = "html"
        email.fail_silently=False
        email.send()
        return redirect ("password_reset_done")
    return render(request, 'accounts/password_reset.html')

def choose_usertype(request):
    user = request.user
    if request.method=="GET":
        if not user.is_authenticated:
            return redirect("account:login")
        
        if user.is_staff:
            return redirect("/admin")
        
        if user.is_patient:
            return redirect("Management_system:patientdashboard")
        if user.is_doctor:
            return redirect("doctor:doctor-dashboard")
    
    if request.method=="POST":
        type = request.POST.get("usertypeoptions")
        licenses = request.POST.get("license")
        if len(licenses) != 10 or not licenses.startswith("NP"):
            messages.error(request, 'Please Enter Valid License Data!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if User.objects.filter(license_number = licenses).exists():
            messages.error(request, 'Doctor with this license data already registered !')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if type =="patient":
            user.is_patient=True
            user.is_doctor=False
            user.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if type=="doctor":
            user.is_patient=False
            user.license_number =licenses
            user.is_doctor=True
            user.save()
            for i in weekday:
                WeekDayAvailable.objects.create(name=i,user=user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'accounts/choose_usertype.html')


