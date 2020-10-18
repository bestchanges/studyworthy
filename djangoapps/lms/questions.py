from typing import TYPE_CHECKING

from django import forms
from django.utils.translation import ugettext_lazy as _

if TYPE_CHECKING:
    from djangoapps.lms.models import Question


class StringType:
    label = _('Строка')

    @classmethod
    def form_field(cls, question: 'Question') -> forms.Field:
        return forms.CharField(
            label=question.text,
            required=question.required,
            max_length=200,
            help_text=cls.label
        )


class IntegerType:
    label = _('Целое число')

    @classmethod
    def form_field(cls, question: 'Question') -> forms.Field:
        return forms.CharField(
            label=question.text,
            required=question.required,
            max_length=200,
            help_text=cls.label
        )