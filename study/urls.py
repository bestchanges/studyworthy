from django.urls import path
from . import views

app_name = 'study'
urlpatterns = [
    path('', views.index, name='index'),

    path('courses/', views.courses_list, name='courses'),
    path('courses/<int:pk>/', views.course, name='course'),

    path('category/<int:pk>/', views.category, name='category'),

    path('study/<int:pk>/', views.study, name='study'),
    path('study/<int:pk>/<int:unit_pk>', views.study_unit, name='study_unit'),

    path('user/', views.user, name='user'),
    path('user/study', views.user_study, name='user_study_session'),
    path('user/settings', views.user_settings, name='user_settings'),
    path('upload', views.upload, name='upload'),
    path('upload1', views.DocumentCreateView.as_view(), name='upload1'),
]
