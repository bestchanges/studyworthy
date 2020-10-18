import json

from django import forms

from . import questions
from .models import Lesson, Question, LessonResponse

import logging

logger = logging.getLogger(__name__)

class StudentResponseForm(forms.ModelForm):
    """Form with response on Lesson Questions"""

    prefix = 'lms-q'

    def __init__(self, *args, lesson: Lesson = None, **kwargs):
        super(StudentResponseForm, self).__init__(*args, **kwargs)
        for question in lesson.questions.all():  # type: Question
            question_type = questions.ALL_TYPES.get(question.type)
            if not question_type:
                logger.error(f'Unknown question type "{question.type}". '
                             f'Available types {questions.ALL_TYPES.keys()}')
                continue
            question_type.fill_form(question, self)

    class Meta:
        model = LessonResponse
        fields = ['id']

    def save(self, commit=True):
        instance: LessonResponse = self.instance
        instance.answers_json = json.dumps(self.cleaned_data, indent=4)
        return super().save(commit)
