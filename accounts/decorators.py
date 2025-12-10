
from django.shortcuts import redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied




def only_non_authorized(func):
    def wrap(request,*args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_patient:
                return redirect("Management_system:patientdashboard")
            elif user.is_doctor:
                return redirect("doctor:doctor-dashboard")
            else:
                return redirect("accounts:choose_usertype")
        else:
            return func(request,*args, **kwargs)
    return wrap



def allow_only_user(user_type):
    def deco(function):
        def wrap(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("accounts:login")
            
            if not user.is_doctor and not user.is_patient:
                return redirect("accounts:choose_usertype")

            if user.is_staff or user.is_superuser:
                return function(request, *args, **kwargs)

            if user_type=="doctor" and user.is_doctor:
                return function(request, *args, **kwargs)

            if user_type=="patient" and user.is_patient:
                return function(request, *args, **kwargs)

            raise Http404("Page not found .")

        return wrap
    return deco

