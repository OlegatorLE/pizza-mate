from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
                  path("admin/", admin.site.urls),
                  path("", include("pizza.urls", namespace="pizza")),
                  path("accounts/", include("django.contrib.auth.urls")),
              ] + static(settings.STATIC_URL,
                         document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
