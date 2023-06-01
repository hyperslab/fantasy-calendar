from django.shortcuts import redirect
from django.urls import path, reverse
from . import views


app_name = 'fantasycalendar'
urlpatterns = [
    path("", lambda req: redirect(reverse('fantasycalendar:world-index'))),
    path("worlds/", views.WorldIndexView.as_view(), name="world-index"),
    path("worlds/<int:pk>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("worlds/new/", views.WorldCreateView.as_view(), name="world-create"),
    path("worlds/<int:pk>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("worlds/<int:world_key>/calendars/<int:pk>/", views.CalendarDetailView.as_view(), name="calendar-detail"),
    path("worlds/<int:world_key>/calendars/new/", views.CalendarCreateView.as_view(), name="calendar-create"),
    path("worlds/<int:world_key>/calendars/<int:pk>/edit/", views.CalendarUpdateView.as_view(), name="calendar-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:pk>/",
         views.TimeUnitDetailView.as_view(), name="time-unit-detail"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/new/", views.TimeUnitCreateView.as_view(),
         name="time-unit-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:pk>/edit/",
         views.TimeUnitUpdateView.as_view(), name="time-unit-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:pk>/instances/<int:iteration>/",
         views.TimeUnitInstanceDetailView.as_view(), name="time-unit-instance-detail"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/events/<int:pk>/", views.EventDetailView.as_view(),
         name="event-detail"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/events/new/", views.EventCreateView.as_view(),
         name="event-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/events/<int:pk>/edit/", views.EventUpdateView.as_view(),
         name="event-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-formats/<int:pk>/",
         views.DateFormatDetailView.as_view(), name="date-format-detail"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-formats/new/", views.DateFormatCreateView.as_view(),
         name="date-format-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-formats/<int:pk>/edit/",
         views.DateFormatUpdateView.as_view(), name="date-format-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/display-configs/new/",
         views.DisplayConfigCreateView.as_view(), name="display-config-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/display-configs/<int:pk>/edit/",
         views.DisplayConfigUpdateView.as_view(), name="display-config-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-bookmarks/new/",
         views.DateBookmarkCreateView.as_view(), name="date-bookmark-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-bookmarks/<int:pk>/edit/",
         views.DateBookmarkUpdateView.as_view(), name="date-bookmark-update"),
]
