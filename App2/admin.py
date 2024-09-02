from django.contrib import admin

# Register your models here.
from .models import usrData,Course,cart,AdminData

admin.site.register(usrData)

admin.site.register(Course)

admin.site.register(cart)

admin.site.register(AdminData)
