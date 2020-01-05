from django.urls import path
from . import views

app_name = 'campus'

urlpatterns = [
    path('', views.index, name='index'),
    path('learn/<learning_code>', views.learning_view, name='learning'),
    path('learn/<learning_code>/<unit_slug>', views.lesson_view, name='lesson'),
]
