from email.policy import default
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="",required=True,widget=forms.TextInput(attrs={'type': 'text','placeholder':'First Name'}))
    last_name = forms.CharField(label="",required=True,widget=forms.TextInput(attrs={'type': 'text','placeholder':'Last Name'}))
    email =  forms.CharField(label="",required=True,widget=forms.TextInput(attrs={'type': 'email','placeholder':'youremail@gmail.com'}))
  
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '********',
    }), min_length=8)
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '*********',
    }))
    term = forms.BooleanField(required=True)
    

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'term','password1','password2')

        
    def __init__(self, *args, **kargs):
        super(RegistrationForm, self).__init__(*args, **kargs)
       
        self.fields['term'].widget.attrs.update({'id': 'term_cond'})

class GoogleSignupForm(forms.Form):
    frequency=(
        ('isPatient','isPatient'),
        ('isDoctor','isDoctor'),
       
    )
    user_type = forms.ChoiceField(required=False, choices=frequency)

    def signup(self, request, user):
        # usertype = self.cleaned_data['user_type']
        # if usertype == "isPatient":
        #     user.is_patient=True
        # else:
        user.is_doctor=True
        user.save()