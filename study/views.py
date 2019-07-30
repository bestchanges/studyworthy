from django.shortcuts import render

from .models import Course


def index(request):
    active_courses = Course.objects.filter(state__in=('active',))
    return render(request, 'study/index.html', {'courses': active_courses})


def category(request, pk):
    return render(request, 'study/category.html', {})


def courses_list(request):
    return render(request, 'study/courses_list.html', {})


def course(request, pk):
    return render(request, 'study/course.html', {})


def study(request, pk):
    return render(request, 'study/study.html', {})


def study_unit(request, pk, unit_pk):
    return render(request, 'study/study_unit.html', {})


def user(request):
    return render(request, 'study/user.html', {})


def user_study(request):
    return render(request, 'study/user_study.html', {})


def user_settings(request):
    return render(request, 'study/user_settings.html', {})
