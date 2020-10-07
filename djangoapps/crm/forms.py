from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse

from djangoapps.crm.models import my_organization
from djangoapps.erp.models import Order, Person, Product


class SingleCourseProductOrderForm(forms.Form):
    product_code = forms.CharField(required=True, widget=forms.HiddenInput)
    user_pk = forms.CharField(required=False, widget=forms.HiddenInput)
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
        client_phone = self.cleaned_data.get('phone')
        if person:
            if not person.phone and client_phone:
                person.phone = self.client_phone
                person.save()
        else:
            person = Person.objects.create(
                email=email,
                phone=client_phone,
            )
            person.full_name = self.cleaned_data.get('name')
            person.save()
        return person

    def create_order(self) -> Order:
        """
        Create client user from form data. Also creates person model.

        :return: ClientOrder with state == None. Update to NEW to start order processing
        """
        assert self.is_valid()

        product = Product.objects.get(code=self.cleaned_data['product_code'])
        person = self._get_or_create_person()

        phone = self.cleaned_data["phone"]
        name = self.cleaned_data["name"]
        comment_items = [
            f'Phone: {phone}' if phone and phone != person.phone else None,
            f'Name: {name}' if name and name != person.full_name else None,
            self.cleaned_data.get('comment'),
        ]
        client_order = Order.objects.create(
            buyer=person,
            seller=my_organization(),
            currency=product.price.currency,
            comment='\n'.join([item for item in comment_items if item])
        )
        client_order.add_item(product, 1)
        client_order.save()

        if client_order.amount.amount == 0:
            # free product fulfill immediately
            fulfill_on = Order.FulfillOn.CREATED
        else:
            # priced product fulfill after payment
            fulfill_on = Order.FulfillOn.ORDER_PAYED_FULL
        client_order.fulfill_on = fulfill_on
        client_order.product = product
        client_order.save()

        return client_order
