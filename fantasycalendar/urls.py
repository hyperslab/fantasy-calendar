from django.urls import path
from . import views


app_name = 'fantasycalendar'
urlpatterns = [
    path("", views.WorldIndexView.as_view(), name="world-index"),
    path("<int:pk>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("<int:world_key>/<int:pk>/", views.CalendarDetailView.as_view(), name="calendar-detail"),
    path("new/", views.WorldCreateView.as_view(), name="world-create"),
    path("<int:world_key>/new/", views.CalendarCreateView.as_view(), name="calendar-create"),
    path("<int:world_key>/<int:calendar_key>/new/", views.TimeUnitCreateView.as_view(), name="time-unit-create"),
    path("<int:pk>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("<int:world_key>/<int:pk>/edit/", views.CalendarUpdateView.as_view(), name="calendar-update"),
    path("<int:world_key>/<int:calendar_key>/<int:pk>/edit/", views.TimeUnitUpdateView.as_view(), name="time-unit-update"),
]
