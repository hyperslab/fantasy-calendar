from django.urls import path
from . import views


app_name = 'fantasycalendar'
urlpatterns = [
    path("", views.WorldIndexView.as_view(), name="world-index"),
    path("<int:pk>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("<int:world_key>/<int:pk>/", views.CalendarDetailView.as_view(), name="calendar-detail"),
]
