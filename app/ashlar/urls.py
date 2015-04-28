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
    # Examples:
    # url(r'^$', 'ashlar.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
]
