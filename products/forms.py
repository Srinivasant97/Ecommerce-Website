from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P','PayPal')
)

class CheckoutForm(forms.Form):
    street_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Street Name',
        'class':'form-control'
    }))
    apartment_no = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'placeholder': 'House No',
        
    }))
    country = CountryField(blank_label='Select Country').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100',
        'id':'zip'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option= forms.ChoiceField(widget=forms.RadioSelect(),choices=PAYMENT_CHOICES)
