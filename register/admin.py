from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'currency', 'balance', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('currency', 'balance')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom fields', {
            'classes': ('wide',),
            'fields': ('email', 'currency', 'balance', 'is_staff', 'is_superuser'),
        }),
    )



admin.site.register(CustomUser, CustomUserAdmin)



# Register your models here.
