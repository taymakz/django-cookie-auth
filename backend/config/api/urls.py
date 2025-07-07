from django.urls import include, path

urlpatterns = [
    path("account/", include("apps.account.urls.frontend")),
    path("sms-service/", include("apps.sms_service.urls.frontend")),
]
