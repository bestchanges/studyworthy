from django.urls import path
from . import views

app_name = 'campus'

urlpatterns = [
    path('', views.index, name='index'),

    path('courses/', views.courses_list, name='courses'),
    path('courses/<int:pk>/', views.course, name='course'),

    path('learn/<int:pk>/', views.study, name='study'),
    path('learn/<int:pk>/<int:unit_pk>', views.study_unit, name='study_unit'),

    path('user/', views.user, name='user'),
    path('user/settings', views.user_settings, name='user_settings'),
]
