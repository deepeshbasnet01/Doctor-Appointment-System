from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"
urlpatterns = [
 path('', views.login, name='login'),
 path('logout/', views.logout, name='logout'),
 path('register/', views.register, name='register'),
 path('doctor-register/', views.doctor_register, name='doctor-register'),
 path('forget-password/', views.forget_password, name='forget-password'),
  path('choose_usertype/', views.choose_usertype, name='choose_usertype'),

path('password_reset/',auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
path('password-reset-complete',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),


]
