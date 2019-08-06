from django.forms import ModelForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Course, Document


def index(request):
    active_courses = Course.objects.filter(state__in=('active',))
    return render(request, 'study/index.html', {'courses': active_courses})


def category(request, pk):
    return render(request, 'study/category.html', {})


def courses_list(request):
    return render(request, 'study/courses_list.html', {})


def course(request, pk):
    course = Course.objects.get(pk=pk)
    return render(request, 'study/course.html', {'course': course})


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


def upload(request):
    class DocumentForm(ModelForm):
        class Meta:
            model = Document
            fields = ['upload']
    documents = Document.objects.all()
    context = {
        'documents': documents,
        'form': DocumentForm(),
    }
    return render(request, 'study/document_form.html', context)


class DocumentCreateView(CreateView):
    model = Document
    fields = ['upload']
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = Document.objects.all()
        context['documents'] = documents
        return context
