from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.urls import reverse

from djangoapps.erp.models import ClientOrder, Person, Product


class SingleCourseProductOrderForm(forms.Form):
    product_code = forms.CharField(required=True) #, widget=forms.HiddenInput)
    user_pk = forms.CharField(required=False) #, widget=forms.HiddenInput)
    name = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=30, required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(
            self,
            *args,
            required_fields=('name', 'email'),
            show_fields=('name', 'email', 'phone'),
            person: Person = None,
            product: Product = None,
            **kwargs):
        super().__init__(*args, **kwargs)

        show_fields_set = set(show_fields) | {'product_code', 'user_pk'}
        if product:
            self.fields['product_code'].initial = product.code
        if person:
            self.fields['name'].initial = person.full_name
            self.fields['email'].initial = person.email
        for key in required_fields:
            self.fields[key].required = True
        drop_fields = set(self.fields) - show_fields_set
        for key in drop_fields:
            self.fields.pop(key)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_style = 'inline'
        self.helper.form_action = reverse('crm:order_single_product')
        self.helper.add_input(Submit('submit', "Записаться"))
        self.helper.help_text_inline = True
        self.helper.html5_required = True

    def _get_or_create_person(self) -> Person:
        assert self.is_valid(), 'Should be valid'
        assert self.cleaned_data['email'], 'Must have email'

        if self.cleaned_data.get('person'):
            return Person.objects.get(pk=self.cleaned_data['person'])

        email = self.cleaned_data['email'].lower()
        person = Person.lookup_by_email(email)
        if person:
            if not person.phone and self.client_phone:
                person.phone = self.client_phone
                person.save()
        else:
            person = Person.objects.create(
                email=email,
                phone=self.cleaned_data.get('phone'),
            )
            person.name = self.cleaned_data.get('name')
        return person

    def create_order(self) -> ClientOrder:
        assert self.is_valid()

        product = Product.objects.get(code=self.cleaned_data['product_code'])
        # if it's free product then let's fulfill immediately
        person = self._get_or_create_person()

        client_order = ClientOrder.objects.create(
            client=person,
            currency=product.price.currency,
            comment=self.cleaned_data.get('comment')
        )
        client_order.add_item(product, 1)
        client_order.save()

        if client_order.amount.amount == 0:
            # free product fulfill immediately
            fulfill_on = ClientOrder.FulfillOn.CREATED
        else:
            # priced product fulfill after payment
            fulfill_on = ClientOrder.FulfillOn.ORDER_PAYED_FULL
        client_order.fulfill_on = fulfill_on
        client_order.state = ClientOrder.State.NEW
        client_order.product = product
        client_order.save()

        return client_order
