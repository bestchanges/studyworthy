from django.shortcuts import render

def index(request):
    return render(request, 'app/index.html', {})

def category(request, pk):
    return render(request, 'app/category.html', {})

def courses_list(request):
    return render(request, 'app/courses_list.html', {})

def course(request, pk):
    return render(request, 'app/course.html', {})

def study(request, pk):
    return render(request, 'app/study.html', {})

def study_unit(request, pk, unit_pk):
    return render(request, 'app/study_unit.html', {})

def user(request):
    return render(request, 'app/user.html', {})

def user_study(request):
    return render(request, 'app/user_study.html', {})

def user_settings(request):
    return render(request, 'app/user_settings.html', {})
