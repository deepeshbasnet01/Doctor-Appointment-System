from django.urls import path
from . import views
app_name = "doctor"
urlpatterns = [
path('doctor-dashboard/', views.doctor_dashboard, name='doctor-dashboard'),
path('all-patients/', views.all_patients, name='all-patients'),
path('new-appointment/', views.new_appointment, name='new-appointment'),
path('appointment-detail/<int:id>/', views.appointment_detail, name='appointment-detail'),
path('create-invoice/', views.create_invoice, name='create-invoice'),
path('patient-settings/<int:id>/', views.patient_settings, name='patient-settings'),
path('billing-list/', views.billing, name='billing-list'),
path('invoice-detail/<int:id>/', views.invoice_detail, name='invoice_detail'),
path('download-pdf/<int:id>/', views.pdf_download, name='pdf_download'),
path('doctor-settings/<int:id>/', views.doctor_settings, name='doctor-settings'),
path('user-history/<int:id>/', views.UserHistory, name='user_history'),
path('doc-user-history/<int:id>/<int:code>/', views.user_history_detail, name='user_history_detail'),
path('searchpatient/', views.search1, name='searchpatient'),

]




