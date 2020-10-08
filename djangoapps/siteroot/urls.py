from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lms/', include('djangoapps.lms_cms.urls')),
    path('crm/', include('djangoapps.crm.urls', namespace='crm')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payments/yk/', include('djangoapps.yandex_kassa.urls', namespace='yandex_kassa')),
    url(r'^', include('cms.urls')),
]

if settings.DJANGO_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
