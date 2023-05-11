from django.shortcuts import redirect
from django.urls import path, reverse
from . import views


app_name = 'fantasycalendar'
urlpatterns = [
    path("", lambda req: redirect(reverse('fantasycalendar:world-index'))),
    path("worlds/", views.WorldIndexView.as_view(), name="world-index"),
    path("worlds/<int:pk>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("worlds/<int:world_key>/calendars/<int:pk>/", views.CalendarDetailView.as_view(), name="calendar-detail"),
    path("worlds/new/", views.WorldCreateView.as_view(), name="world-create"),
    path("worlds/<int:world_key>/calendars/new/", views.CalendarCreateView.as_view(), name="calendar-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/new/", views.TimeUnitCreateView.as_view(),
         name="time-unit-create"),
    path("worlds/<int:pk>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("worlds/<int:world_key>/calendars/<int:pk>/edit/", views.CalendarUpdateView.as_view(), name="calendar-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:pk>/edit/",
         views.TimeUnitUpdateView.as_view(), name="time-unit-update"),
]
