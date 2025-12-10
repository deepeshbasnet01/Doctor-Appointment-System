from zoneinfo import available_timezones
from django.db import models
from django.contrib.auth.models import  AbstractUser


departments=[
    ('Cardiologist','Cardiologist'),
('Dermatologists','Dermatologists'),
('Emergency Medicine Specialists','Emergency Medicine Specialists'),
('Allergists/Immunologists','Allergists/Immunologists'),
('Anesthesiologists','Anesthesiologists'),
('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
]

venue = [('Itahari','Cardiologist'),
('Dermatologists','Dermatologists'),
('Emergency Medicine Specialists','Emergency Medicine Specialists'),
('Allergists/Immunologists','Allergists/Immunologists'),
('Anesthesiologists','Anesthesiologists'),
('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
]






class User(AbstractUser):
    email = models.CharField(max_length=200, unique=True)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    bio = models.TextField(blank=True ,default="")
    availability = models.BooleanField(default=False)
    license_number = models.CharField(max_length=200, unique=True,null=True,blank=True)
    profile_pic= models.ImageField(upload_to='profile_pic/',null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)
    blood_group = models.CharField(max_length=20,null=True,blank=True)
    sex = models.CharField(max_length=50,null=True,blank=True)
    mobile = models.CharField(max_length=20,null=True,blank=True)
    specialist = models.CharField(max_length=100,choices=departments,null=True,blank=True)
    working_hospital =  models.CharField(max_length=100,null=True,blank=True)
    working_location =  models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    
    available_days = models.CharField(max_length=100,null=True,blank=True)
    weight= models.CharField(max_length=10,null=True,blank=True)
    title=models.CharField(max_length=100,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def get_image(self):
       
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return ''
    
    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    @property
    def get_ratings(self):
        alls = self.all_rates.all()
        total_rating =0
        for i in alls:
            total_rating+=i.my_rate
        return total_rating/alls.count() if total_rating != 0 else  0

class RatingModel(models.Model):
    of_user = models.OneToOneField(User, on_delete=models.CASCADE)
    rate = models.IntegerField(null=True)

class MyRate(models.Model):
    of_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="all_rates")
    my_rate = models.IntegerField(null=True)
    date_created=models.DateTimeField(auto_now_add=True)
    by_user =models.ForeignKey(User, related_name="my_rates",null=True,on_delete=models.CASCADE)
    
    

class WeekDayAvailable(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available_from = models.TimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    available_to = models.TimeField(auto_now=False, auto_now_add=False,null=True,blank=True)