from django.shortcuts import render

def courses(request):
    return render(request, 'app/courses.html', {})

def start_course(request, pk):
    return render(request, 'app/start_course.html', {})

def study(request):
    return render(request, 'app/study.html', {})

def study_manage(request, pk):
    return render(request, 'app/study_manage.html', {})
