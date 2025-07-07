from django.conf import settings
from django.urls import path, include
import debug_toolbar


urlpatterns = [
    path("api/", include("config.api.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
