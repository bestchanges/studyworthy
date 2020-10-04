from django.urls import path
from djangoapps.lms_cms import views

app_name = 'lms_cms'

urlpatterns = [
    path('comment/add', views.comment_add, name='comment_reply'),
    path('', views.student_kabinet, name='student_kabinet'),
    path('student/<int:student_id>/', views.student_flow, name='student_flow'),
    path('lesson/<int:student_lesson_id>/', views.student_lesson, name='student_lesson'),
    path('lesson/<int:student_lesson_id>/mark-completed', views.attendance_completed, name='attendance-completed'),
]
