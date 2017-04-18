"""bigrs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from maps import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name="index"),
    url(r'^theme', views.theme),
    url(r'^geojson', views.geojson),
    url(r'^vector', views.vector),
    url(r'^auth', views.auth),
    url(r'^contador/(?P<contador_id>\d+)/$', views.contador),
    url(r'^teclado$', views.teclado),
    url(r'^lista', views.lista_contagens),
    url(r'^get_player$', views.get_player),
    url(r'^set_player$', views.set_player),
    url(r'^nova_contagem', views.nova_contagem),
    url(r'^conta$', views.conta),
    url(r'^logout', views.log_out),
    url(r'^reverse_geocode', views.reverse_geocode),
    url(r'^reverse', views.reverse),
    url(r'^search', views.search),
    url(r'^geocode', views.geocode),
    url(r'^socialauth-error', views.social_error),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
urlpatterns += staticfiles_urlpatterns()
