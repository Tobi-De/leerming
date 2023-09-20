from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse
from django.http import HttpResponseRedirect


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("schema-viewer/", include("schema_viewer.urls")),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("leerming.profiles.urls", namespace="profiles")),
    path("cards/", include("leerming.cards.urls", namespace="cards")),
    path(
        "", lambda request: HttpResponseRedirect(reverse("cards:index")), name="home"
    ),  # TODO: replace by a landing page at some point
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
