from django.urls import path, include
from .rest_api_v1 import router
from . import views

app_name = 'lms'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('', views.index, name='index'),

    path('courses/', views.courses_list, name='courses'),
    path('courses/<int:pk>/', views.course, name='course'),

    path('category/<int:pk>/', views.category, name='category'),

    path('lms/<int:pk>/', views.study, name='study'),
    path('lms/<int:pk>/<int:unit_pk>', views.study_unit, name='study_unit'),

    path('user/', views.user, name='user'),
    path('user/lms', views.user_lms, name='user_lms_session'),
    path('user/settings', views.user_settings, name='user_settings'),
    path('upload', views.upload, name='upload'),
    path('upload1', views.DocumentCreateView.as_view(), name='upload1'),
]
