from django.forms import ModelForm

from djangoapps.erp.models import Order
from djangoapps.erp.models.erp import Client


class ClientOrderForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for key in ['client_name', 'client_email']:
            self.fields[key].required = True

    class Meta:
        model = Order
        fields = ['client_name', 'client_email', 'client_phone', 'comment']
