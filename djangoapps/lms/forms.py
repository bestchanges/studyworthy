from django import forms

from .models import Lesson, Question


class LessonQuestionsForm(forms.BaseForm):
    base_fields = {}

    def __init__(self, *args, lesson: Lesson = None, **kwargs):
        super().__init__(*args, **kwargs)
        for question in lesson.questions.all():  # type: Question
            self.fields[question.code] = self.question_field(question)

    def question_field(self, question: Question):
        """Build form field for the question type defined in question."""
        type_class = question.Types.all[question.type]
        return type_class.form_field(question)
