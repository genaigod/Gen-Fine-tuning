# Register your models here.
from django.contrib import admin


from .models import ApiUser

custome_field = ['username']
black_list = custome_field + ['password', "headimgurl"]

class ApiUserModelAdmin(admin.ModelAdmin):

    list_display = [field.name for field in ApiUser._meta.fields if field.name not in black_list]

    @admin.display(description='Last Login', ordering=True)
    def formatted_last_login(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None
    list_display = custome_field + list_display

    def save_model(self, request, obj, form, change):
        print(f"change:{change}, form.cleaned_data['password']:{form.cleaned_data['password']}")
        old_obj = self.get_object(request, obj.uid)

        if not change or form.cleaned_data['password'] != old_obj.password:
            obj.set_password(form.cleaned_data['password'])
            super().save_model(request, obj, form, change)
        else:
            print(old_obj.password)
            obj.password = old_obj.password
            super().save_model(request, obj, form, change)

# Register your models here.
# admin.site.register(ApiUser)
admin.site.register(ApiUser, ApiUserModelAdmin)
# admin.site.register(Role)

