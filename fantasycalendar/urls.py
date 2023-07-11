from django.shortcuts import redirect
from django.urls import path, reverse, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework import routers
from . import api_views


router = routers.DefaultRouter()
router.register('worlds', api_views.WorldViewSet, 'world')
router.register('calendars', api_views.CalendarViewSet, 'calendar')
router.register('timeunits', api_views.TimeUnitViewSet, 'timeunit')
router.register('events', api_views.EventViewSet, 'event')
router.register('dateformats', api_views.DateFormatViewSet, 'dateformat')
router.register('displayconfigs', api_views.DisplayConfigViewSet, 'displayconfig')
router.register('datebookmarks', api_views.DateBookmarkViewSet, 'datebookmark')

app_name = 'fantasycalendar'
urlpatterns = [
    path("", lambda req: redirect(reverse('fantasycalendar:world-index'))),
    path("accounts/login/", auth_views.LoginView.as_view(template_name=app_name + "/login.html",
                                                         next_page='fantasycalendar:world-index'), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(template_name=app_name + "/login.html",
                                                           next_page='fantasycalendar:world-index'), name="logout"),
    path("accounts/new/", views.UserCreateView.as_view(), name="user-create"),
    path("api/", include(router.urls)),
    path("api/timeunitbaseinstances/", api_views.TimeUnitBaseInstances.as_view()),
    path("api/timeunitinstancedisplayname/", api_views.TimeUnitInstanceDisplayName.as_view()),
    path("api/timeunitequivalentiteration/", api_views.TimeUnitEquivalentIteration.as_view()),
    path("worlds/", views.WorldIndexView.as_view(), name="world-index"),
    path("worlds/<int:pk>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("worlds/new/", views.WorldCreateView.as_view(), name="world-create"),
    path("worlds/<int:pk>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("worlds/<int:world_key>/calendars/<int:pk>/", views.CalendarDetailView.as_view(), name="calendar-detail"),
    path("worlds/<int:world_key>/calendars/new/", views.CalendarCreateView.as_view(), name="calendar-create"),
    path("worlds/<int:world_key>/calendars/<int:pk>/edit/", views.CalendarUpdateView.as_view(), name="calendar-update"),
    path("worlds/<int:world_key>/calendars/<int:pk>/calendar/", views.CalendarCalendarView.as_view(),
         name="calendar-calendar"),
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
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:timeunit_key>/date-formats/<int:pk>/",
         views.DateFormatDetailView.as_view(), name="date-format-detail"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:timeunit_key>/date-formats/new/",
         views.DateFormatCreateView.as_view(), name="date-format-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/time-units/<int:timeunit_key>/date-formats/<int:pk>/"
         "edit/", views.DateFormatUpdateView.as_view(), name="date-format-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/display-configs/new/",
         views.DisplayConfigCreateView.as_view(), name="display-config-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/display-configs/<int:pk>/edit/",
         views.DisplayConfigUpdateView.as_view(), name="display-config-update"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-bookmarks/new/",
         views.DateBookmarkCreateView.as_view(), name="date-bookmark-create"),
    path("worlds/<int:world_key>/calendars/<int:calendar_key>/date-bookmarks/<int:pk>/edit/",
         views.DateBookmarkUpdateView.as_view(), name="date-bookmark-update"),
]
