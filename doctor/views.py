from wsgiref.util import request_uri
from django.conf import settings
from django.contrib import  messages
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404, render
from Management_system.forms import AppointInvoiceForm, AppointmentForm, AppointmentReportForm, EditDoctorForm, EditPatientForm, InvoiceForm
from accounts.decorators import allow_only_user
from accounts.models import User,WeekDayAvailable
from django.contrib.auth.decorators import login_required
from Management_system.models import Appointment, AppointmentReport, History, Invoice
from django.forms import inlineformset_factory
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q
from django.shortcuts import render
def index_view(request):
    return render(request, 'index.html')

@allow_only_user("doctor")
def doctor_dashboard(request):
    appointments  = Appointment.objects.filter(doctor=request.user)
    app_count = appointments.count()
    billings_count = Invoice.objects.filter(doctor=request.user).count()
    my_patients = set()
    for i in appointments:
        my_patients.add(i.patient)
    
    context={"appointments":appointments,"app_count":app_count,"my_patients":len(my_patients),"billings_count":billings_count}
    return render(request, 'doctor-dashboard.html',context)
    
    
@allow_only_user("doctor")
def all_patients(request):
    appointments  = Appointment.objects.filter(doctor=request.user)
    my_patients = set()
    for i in appointments:
        my_patients.add(i.patient)
    context = {'patients': my_patients}
    return render(request, 'all-patients.html',context)


@allow_only_user("doctor")
def new_appointment(request):
    appointments  = Appointment.objects.filter(doctor=request.user)
    context={"appointments":appointments}
    return render(request, 'new-appointment.html',context)

@allow_only_user("doctor")
def UserHistory(request,id):
    user = get_object_or_404(User,id=id)
    histories  = History.objects.filter(patient=user)
    context={"histories":histories,'user':user}
    return render(request, 'medical_history.html',context)


@allow_only_user("doctor")
def user_history_detail(request,id,code):
    user = get_object_or_404(User,id=id)
    history  =get_object_or_404(History,id=code)
    files = history.hisotry_files.all()
    context={"history":history,'user':user,'files':files}
    return render(request, 'medical_history_detail.html',context)

from django.core.mail import send_mail
@allow_only_user("doctor")
def appointment_detail(request,id):
    invoice_form = AppointInvoiceForm()
    
    appointment = get_object_or_404(Appointment,id=id)
    app_form = AppointmentForm(instance=appointment)
    report = AppointmentReport.objects.filter(appointment=appointment).first()
    form = AppointmentReportForm() if not report else  AppointmentReportForm(instance=report) 

    if "update_app" in request.POST:
        app_form = AppointmentForm(request.POST,instance = appointment)
        app_form.save()
        send_mail(
            'Appointment Updated',
            f'Your Appointment has been updated by {appointment.doctor} . Please check detail from website .',
                settings.EMAIL_HOST_USER,
            [appointment.patient.email],
            fail_silently=False,
            )
        messages.success(request,"Successfully Updated Appointment ")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if "create_report" in request.POST:
        form = AppointmentReportForm(request.POST,instance=report)
        if form.is_valid():
            fr = form.save(commit=False)
            fr.appointment = appointment
            fr.doctor =  appointment.doctor
            fr.patient = appointment.patient
            # if request.FILES:
            #     fr.profile_pic=request.FILES['propic']
            fr.save()
            messages.success(request,"Successfully added Report")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if "start_appointment" in request.POST:
        appointment.status = "In Progress"
        appointment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if "deliver_appointment" in request.POST:
        appointment.status = "Delivered"
        appointment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if "create_invoice" in request.POST:
        invoice_form = AppointInvoiceForm(request.POST)
        f =invoice_form.save(commit=False)
        f.doctor = request.user
        f.patient = appointment.patient
        f.of_appointment = appointment
        f.save()
        messages.success(request,"Successfully Added Invoice")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
    context = {"appointment":appointment,"form":form,"invoice_form":invoice_form,"app_form":app_form}
    return render(request, 'appointment_detail.html',context)


@allow_only_user("doctor")
def create_invoice(request):
    form =InvoiceForm()
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.doctor = request.user
            f.save()
            messages.success(request,"Successfully Added Invoice")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context ={"form":form}
    return render(request, 'create-invoice.html',context)

@allow_only_user("doctor")
def invoice_detail(request,id):
    invoice = get_object_or_404(Invoice ,id=id)
    context ={"invoice":invoice}
    return render(request, 'invoice_detail.html',context)


@allow_only_user("doctor")
def billing(request):
    invoices = Invoice.objects.filter(doctor=request.user)
    context ={"invoices":invoices}
    return render(request, 'billing-list.html',context)



@allow_only_user("doctor")
def doctor_settings(request,id):
    DayFormSet = inlineformset_factory(User,WeekDayAvailable,
    fields=('name','available_from','available_to'),
    extra=0)
    user = User.objects.filter(is_doctor=True).get(id=id)
    formset = DayFormSet(instance =user)
    can_edit = request.user == user or request.user.is_staff 
    form = EditDoctorForm(instance=request.user)
    if request.method == 'POST':
        if not can_edit: 
            messages.error(request,"You don't have permission for this ")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if "update_info" in request.POST:
            form = EditDoctorForm(request.POST,instance=request.user)
            if form.is_valid():
                avail = True if request.POST.get("availability") else False        
                fr = form.save(commit=False)
                fr.availability = avail
                if request.FILES:
                    fr.profile_pic=request.FILES['propic']
                fr.save()
                messages.success(request,"Successfully edited your information ")
                
        if "update_time" in request.POST:
            formset = DayFormSet(request.POST,instance =user)
            if formset.is_valid():
                formset.save()
            else:
                print(formset.errors)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                


    context={"form":form,"user":user,"can_edit":can_edit,"formset":formset}
    return render(request, 'doctor-settings.html',context)



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def pdf_download(request, id):
    invoice =  get_object_or_404(Invoice,id=id)
    data = {
    'invoice':invoice,
    'domain':request.META['HTTP_HOST']
    }
    pdf = render_to_pdf('invoice_pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')
from django.core.exceptions import PermissionDenied

@allow_only_user("doctor")
def patient_settings(request,id):
    user = User.objects.filter(is_patient=True).get(id=id)
    form = EditPatientForm(instance=user)
    can_edit = request.user == user or request.user.is_staff 
 
    if request.method == 'POST':
        if can_edit:
            form = EditPatientForm(request.POST,instance=request.user)
            if form.is_valid():
                fr = form.save(commit=False)
                print(request.FILES)
                if request.FILES:
                    fr.profile_pic=request.FILES['propic']
                fr.save()
                messages.success(request,"Successfully edited your information ")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            
            raise PermissionDenied
    context={"form":form,"user":user,"can_edit":can_edit}
    return render(request, 'patient-settings.html',context)

def search1(request):

    results = []

    if request.method == "GET":

        query = request.GET.get('search1')

        if query == '':

            query = 'None'

        results = User.objects.filter(Q(first_name__icontains=query)| Q(username__icontains=query)|Q(email__icontains=query) )

    return render(request, 'searchpatient.html', {'query': query, 'results': results})
