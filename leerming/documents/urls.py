from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload, name="upload"),
    path("get-form/", views.get_form, name="get_form"),
    path("select/", views.select, name="select"),
    path("upload-status/<str:task_id>/", views.upload_status, name="upload_status"),
    path(
        "upload-progress/<str:task_id>/", views.upload_progress, name="upload_progress"
    ),
]
