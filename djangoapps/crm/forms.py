from django.forms import ModelForm

from crm.models.crm_models import Enrollment


class EnrollmentForm(ModelForm):
    class Meta:
        model = Enrollment
        fields = ['name', 'email', 'phone', 'comment']
