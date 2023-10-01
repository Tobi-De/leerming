from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import path, include, reverse

from leerming.profiles.decorators import profile_required

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("schema-viewer/", include("schema_viewer.urls")),
    path("account/", include("allauth.urls")),
    path(
        "profiles/",
        decorator_include(
            login_required, "leerming.profiles.urls", namespace="profiles"
        ),
    ),
    path(
        "flashcards/",
        decorator_include(
            (login_required, profile_required),
            "leerming.flashcards.urls",
            namespace="flashcards",
        ),
    ),
    path(
        "reviews/",
        decorator_include(login_required, "leerming.reviews.urls", namespace="reviews"),
    ),
    path(
        "",
        lambda request: HttpResponseRedirect(reverse("flashcards:index")),
        name="home",
    ),  # TODO: replace by a landing page at some point
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
