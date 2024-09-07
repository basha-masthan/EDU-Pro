from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(usrData)

admin.site.register(Course)

admin.site.register(cart)

admin.site.register(AdminData)

admin.site.register(Contact_data)