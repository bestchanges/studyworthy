from django.forms import ModelForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from lms.models.base import Document
from lms.models.content import Course


def index(request):
    user = request.user
    # if user.is_authenticated:
    #     return redirect(dashboard)

    active_courses = Course.objects.filter(state__in=('active',))
    return render(request, 'campus/index.html', {'courses': active_courses})


def dashboard(request):
    return render(request, 'campus/category.html', {})


def courses_list(request):
    return render(request, 'campus/courses_list.html', {})


def course(request, pk):
    course = Course.objects.get(pk=pk)
    return render(request, 'campus/course.html', {'course': course})


def study(request, pk):
    return render(request, 'campus/study.html', {})


def study_unit(request, pk, unit_pk):
    return render(request, 'campus/study_unit.html', {})


def user(request):
    return render(request, 'campus/user.html', {})


def user_lms(request):
    return render(request, 'campus/user_study.html', {})


def user_settings(request):
    return render(request, 'campus/user_settings.html', {})


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
    return render(request, 'campus/document_form.html', context)


class DocumentCreateView(CreateView):
    model = Document
    fields = ['upload']
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = Document.objects.all()
        context['documents'] = documents
        return context
