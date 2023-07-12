from django.shortcuts import redirect
from django.urls import path, reverse
from . import views
from django.contrib.auth import views as auth_views


app_name = 'accounts'
urlpatterns = [
    path("", lambda req: redirect(reverse('accounts:login'))),
    path("login/", auth_views.LoginView.as_view(template_name=app_name + "/login.html",
                                                next_page='fantasycalendar:world-index'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name=app_name + "/login.html",
                                                  next_page='fantasycalendar:world-index'), name="logout"),
    path("new/", views.UserCreateView.as_view(), name="user-create"),
]
