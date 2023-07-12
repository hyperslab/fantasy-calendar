from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import User
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(auth_admin.UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ["username"]


admin.site.register(User, UserAdmin)
