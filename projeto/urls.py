from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^experiencias/', include('experiencias.urls')),
    url(r'^admin/', admin.site.urls),
]