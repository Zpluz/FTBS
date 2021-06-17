from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Candidate)
admin.site.register(Airplane)
admin.site.register(Airline)
admin.site.register(Flight)
admin.site.register(Seat)
admin.site.register(Order)
