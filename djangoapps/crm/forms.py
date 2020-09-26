from django.forms import ModelForm

from djangoapps.crm.models.erp_models import ClientOrder, PaymentIn


class ClientOrderForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for key in ['client_name', 'client_email']:
            self.fields[key].required = True

    class Meta:
        model = ClientOrder
        fields = ['client_name', 'client_email', 'client_phone', 'comment']


class PaymentInForm(ModelForm):
    class Meta:
        model = PaymentIn
        fields = ['gateway']
