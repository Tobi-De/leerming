from django.urls import path

from . import views

app_name = "gifts"

urlpatterns = [
    path("", views.index, name="index"),
    path("set-recipient/", views.set_recipient, name="set_recipient"),
    path("confirm-send/", views.confirm_send, name="confirm_send"),
    path("cancel-send/", views.cancel_send, name="cancel_send"),
    path("open/<int:pk>/", views.open_gift, name="open"),
]
