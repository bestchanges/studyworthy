from django.urls import path
from djangoapps.lms_cms import views

app_name = 'lms_cms'

urlpatterns = [
    path('comment/add', views.comment_add, name='comment_reply'),
    path('', views.student_kabinet, name='student_kabinet'),
    path('study/<int:flow_id>/', views.flow_view, name='flow-view'),
    path('lesson/<int:flow_lesson_id>/', views.lesson_view, name='flow-lesson-view'),
    path('lesson/<int:participant_lesson_id>/mark-completed', views.attendance_completed, name='attendance-completed'),
]
