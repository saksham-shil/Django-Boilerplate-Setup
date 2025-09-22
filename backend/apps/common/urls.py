from django.urls import path

from . import views


app_name = "common"
urlpatterns = [
    path("api/check", views.check, name="check"),
]
