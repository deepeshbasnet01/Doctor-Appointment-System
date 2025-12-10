from django.contrib import admin
from .models import *
from allauth.socialaccount.models import SocialApp


admin.site.register(User)
admin.site.register(WeekDayAvailable)

admin.site.register(RatingModel)
admin.site.register(MyRate)