from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers

from grout import views

# To get a default set of views, just include grout.urls.urlpatterns in your main app's urls.py
router = routers.DefaultRouter()
router.register('boundaries', views.BoundaryViewSet)
router.register('boundarypolygons', views.BoundaryPolygonViewSet)
router.register('records', views.RecordViewSet)
router.register('recordschemas', views.RecordSchemaViewSet)
router.register('recordtypes', views.RecordTypeViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
]

# Allow login to the browseable API if in debug mode
if settings.DEVELOP:
    urlpatterns.append(url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')))
