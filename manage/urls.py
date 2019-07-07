from django.urls import path
from . import views

app_name = 'manage'
urlpatterns = [
    path('courses/', views.courses, name='courses'),
    path('courses/<int:pk>/start', views.start_course, name='start_course'),

    path('study/', views.study, name='study'),
    path('study/<int:pk>', views.study_manage, name='study_manage')
]
