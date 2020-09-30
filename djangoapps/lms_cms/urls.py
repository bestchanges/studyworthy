from django.urls import path
from djangoapps.lms_cms import views

app_name = 'lms_cms'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('comment/add', views.comment_add, name='comment_reply'),
    path('attendance/<int:attendance_id>/mark-completed', views.attendance_completed, name='attendance-completed'),
]
