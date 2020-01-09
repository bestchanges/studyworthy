from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('course/<code>', views.course_product, name='course_product'),
    path('accepted-ok', views.enrollment_accepted, name='enrollment_accepted'),
    path('dashboard', views.dashboard),
    path('logout', views.logout_view),
    path('', include('django.contrib.auth.urls')),
    path('', include('social_django.urls')),
]
