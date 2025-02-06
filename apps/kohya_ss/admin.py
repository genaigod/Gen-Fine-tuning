# Register your models here.
from django.contrib import admin


from .models import AsyncTask

custome_field = []
black_list =  []

class AsyncTaskModelAdmin(admin.ModelAdmin):

    list_display = [field.name for field in AsyncTask._meta.fields if field.name not in black_list]

    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 50

admin.site.register(AsyncTask, AsyncTaskModelAdmin)

