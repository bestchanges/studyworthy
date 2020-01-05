from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard),
    path('logout', views.logout_view),
    path('', include('django.contrib.auth.urls')),
    path('', include('social_django.urls')),
]
