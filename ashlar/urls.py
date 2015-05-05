from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers

from ashlar import views

router = routers.DefaultRouter()
router.register('record', views.RecordViewSet)
router.register('recordschema', views.RecordSchemaViewSet)
router.register('itemschema', views.ItemSchemaViewSet)
router.register('boundary', views.BoundaryViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
]

# Allow login to the browseable API if in debug mode
if settings.DEVELOP:
    urlpatterns.append(url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')))
if getattr(settings, 'OAUTH2_PROVIDER', None):
    urlpatterns.append(url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')))
