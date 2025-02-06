"""
URL configuration for kohya_ss_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import re

from django.contrib import admin
from django.urls import path, re_path
from django.urls import include
from django.conf.urls.static import static

from django.views import static as view_static
from django.conf.urls import url
from django.views.static import serve

from kohya_ss_admin.views import *
from django.conf import settings

print(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))


def my_static(prefix, view=serve, **kwargs):
    """
    Return a URL pattern for serving files in debug mode.

    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        # ... the rest of your URLconf goes here ...
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    return [
        re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs),
    ]


urlpatterns = [
                  path('__myadmin_/', admin.site.urls),
                  path('auth/', include("apps.api_auth.urls")),
                  path('kohya_ss/', include("apps.kohya_ss.urls")),
                  path('', IndexView.as_view(), name='index'),
                  path('redirect_uri/', SdDdRedirectUrlView.as_view(), name='redirect_uri'),
                  url(r'^static/(?P<path>.*)$', view_static.serve, {'document_root': settings.STATIC_ROOT},
                      name='static'),
              ] + my_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)