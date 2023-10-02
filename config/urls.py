from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import include
from django.urls import path
from django.urls import reverse
from django.views import defaults as default_views

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
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
