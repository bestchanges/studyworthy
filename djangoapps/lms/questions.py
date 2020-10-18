from typing import TYPE_CHECKING

from django import forms
from django.utils.translation import ugettext_lazy as _

if TYPE_CHECKING:
    from djangoapps.lms.models import Question
    from django.forms import BaseForm


ALL_TYPES = {}

def register_type(type_class):
    global ALL_TYPES
    ALL_TYPES[type_class.name] = type_class
    return type_class


class Type:
    name = None
    label = None

    @classmethod
    def fill_form(cls, question: 'Question', form: 'BaseForm'):
        """Add field(s) to the form for this question."""
        raise NotImplemented()

@register_type
class StringType(Type):
    name = 'String'
    label = _('Строка')
    help_text = None

    @classmethod
    def fill_form(cls, question: "Question", form: "BaseForm"):
        form.fields[question.code] = forms.CharField(
            label=question.text,
            required=question.required,
            help_text=cls.help_text
        )


@register_type
class IntegerType(Type):
    name = 'Integer'
    label = _('Целое число')
    help_text = _('Целое число')

    @classmethod
    def fill_form(cls, question: "Question", form: "BaseForm"):
        form.fields[question.code] = forms.IntegerField(
            label=question.text,
            required=question.required,
            help_text=cls.help_text
        )

# INTEGER_FIELD = 'INTEGER_FIELD', _('Целое число')
# SELECT_FIELD = 'SELECT_FIELD', _('Выбор одного из списка')
# MULTISELECT_FIELD = 'MULTISELECT_FIELD', _('Выбор нескольких из списка')
# RADIO_FIELD = 'RADIO_FIELD', _('Радио кнопки')
# CHECKBOXES_FIELD = 'CHECKBOXES_FIELD', _('Чекбоксы')
# URL_FIELD = 'URL_FIELD', _('Ссылка')
# EMAIL_FIELD = 'EMAIL_FIELD', _('Email')
# FILE_FIELD = 'FILE_FIELD', _('Файл')
