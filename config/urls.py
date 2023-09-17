from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from leerming.core.views import index

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", index),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
