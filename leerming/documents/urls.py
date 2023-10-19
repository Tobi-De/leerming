from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("upload", views.upload, name="upload"),

]
