from django.forms import ModelForm

from crm.models.crm_models import Enrollment


class EnrollmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for key in ['name', 'email']:
            self.fields[key].required = True

    class Meta:
        model = Enrollment
        fields = ['name', 'email', 'phone', 'comment']
