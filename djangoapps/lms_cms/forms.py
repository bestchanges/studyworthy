from typing import Optional

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse
from django.utils.translation import (
    ugettext as _,
)

from djangoapps.lms_cms.models import Comment


def create_comment_form(participant, parent: Optional[Comment]):
    if participant.role in [participant.ROLE_TEACHER, participant.ROLE_ADMIN]:
        if parent:
            fields = ['comment', 'file', 'check_result', 'score']
        else:
            fields = ['comment', 'file']
    else:
        if parent:
            fields = ['comment', 'file']
        else:
            fields = ['comment', 'file', 'hide_from_others']
    fields += ['participant', 'parent', 'flow_lesson']
    form = forms.modelform_factory(
        model=Comment,
        fields=fields,
        widgets={
            'participant': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'cols': 30, 'rows': 4}),
            'parent': forms.HiddenInput(),
            'flow_lesson': forms.HiddenInput(),
        }
    )
    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_style = 'inline'
    helper.form_action = reverse('lms_cms:comment_reply')
    helper.add_input(Submit('submit', _('Submit')))
    helper.help_text_inline = True
    helper.html5_required = True
    form.helper = helper
    return form
