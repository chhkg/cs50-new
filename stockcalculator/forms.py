from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Transaction, StockHolding, FiatHolding, CryptoHolding
from .choices import ASSETS, FIATS, TYPES



class DateInput(forms.DateInput):
    input_type = 'date'

""" Transaction search form """
class TransactionSearch(forms.Form):
    
    asset = forms.MultipleChoiceField(label='Asset (Ctrl/Shift to multi-select)', widget=forms.SelectMultiple(attrs={'id': 'asset-search'}), choices=ASSETS, required=False)
    currency = forms.MultipleChoiceField(label='Currency (Ctrl/Shift to multi-select)', widget=forms.SelectMultiple(attrs={'id': 'currency-search'}), choices=FIATS, required=False)
    startdate = forms.DateField(label='Start Date', widget=DateInput(attrs={'id': 'startdate-search'}), required=False,)
    enddate = forms.DateField(label='End Date', widget=DateInput(attrs={'id': 'enddate-search'}), required=False,)
    type = forms.MultipleChoiceField(label='Type (Ctrl/Shift to multi-select)', widget=forms.SelectMultiple(attrs={'id': 'type-search'}), choices=TYPES, required=False)
    symbol = forms.CharField(label='Symbol', widget=forms.TextInput(attrs={'placeholder': 'Symbol', 'id': 'symbol-search'}), max_length=100 , required=False)
    remark = forms.CharField(label='Remark', widget=forms.TextInput(attrs={'placeholder': 'Remark', 'id': 'remark-search'}), max_length=300 , required=False)

    def search(self, user):
        transactions = Transaction.objects.filter(user=user).order_by('-date')
        asset = self.cleaned_data.get('asset')
        currency = self.cleaned_data.get('currency')
        startdate = self.cleaned_data.get('startdate')
        enddate = self.cleaned_data.get('enddate')
        type = self.cleaned_data.get('type')
        symbol = self.cleaned_data.get('symbol')
        remark = self.cleaned_data.get('remark')

        if asset:
            transactions = transactions.filter(asset__in=asset)
        if currency:
            transactions = transactions.filter(currency__in=currency)
        if startdate:
            transactions = transactions.filter(date__gte=startdate)
        if enddate:
            transactions = transactions.filter(date__lte=enddate)
        if type:
            transactions = transactions.filter(type__in=type)
        if symbol:
            transactions = transactions.filter(symbol__icontains=symbol)
        if remark:
            transactions = transactions.filter(remark__icontains=remark)
        return transactions


""" Transaction create form """

class CurrencyTradingWidget(forms.MultiWidget):
    # Custom widget to display two text input boxes in one field.
    def __init__(self, attrs=None):
        widgets = [
            forms.Select(attrs={'class': 'form-control trading-symbol', 'id': 'buycurrency-create'}, choices=FIATS),
            forms.Select(attrs={'class': 'form-control trading-symbol', 'id': 'sellcurrency-create'}, choices=FIATS),
        ]

        # Set the placeholder attribute on the first option element of each dropdown
        for widget, placeholder in zip(widgets, ['Buy Currency', 'Sell Currency']):
            widget.choices.insert(0, ('', placeholder))

        super().__init__(widgets)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
class CryptoTradingWidget(forms.MultiWidget):
    # Custom widget to display two text input boxes in one field.
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'class': 'form-control trading-symbol', 'id': 'buycrypto-create', 'placeholder': 'Buy Crypto Symbol'}),
            forms.TextInput(attrs={'class': 'form-control trading-symbol', 'id': 'sellcrypto-create', 'placeholder': 'Sell Crypto Symbol'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]


class CreateTransaction(forms.Form):

    asset = forms.ChoiceField(label='Asset', widget=forms.Select(attrs={'id': 'asset-create'}), choices=BLANK_CHOICE_DASH + ASSETS)
    currency = forms.ChoiceField(label='Currency', widget=forms.Select(attrs={'id': 'currency-create', 'placeholder': 'Select an option'}), choices=BLANK_CHOICE_DASH + FIATS, required=False)
    date = forms.DateField(label='Date', widget=DateInput(attrs={'id': 'date-create'}), required=True,)
    type = forms.ChoiceField(label='Type', widget=forms.Select(attrs={'id': 'type-create'}), choices=BLANK_CHOICE_DASH + TYPES)
    symbol = forms.CharField(label='Symbol', widget=forms.TextInput(attrs={'placeholder': 'Symbol', 'id': 'symbol-create'}), max_length=100 , required=False,)
    # currencytradingsymbol = CurrencyTradingField(label='Symbol', required=False)
    buyfiatsymbol = forms.ChoiceField(label='Buy Currency', widget=forms.Select(attrs={'id': 'buyfiatsymbol-create', 'placeholder': 'Select an option'}), choices=BLANK_CHOICE_DASH + FIATS, required=False)
    sellfiatsymbol = forms.ChoiceField(label='Sell Currency', widget=forms.Select(attrs={'id': 'sellfiatsymbol-create', 'placeholder': 'Select an option'}), choices=BLANK_CHOICE_DASH + FIATS, required=False)
    buycryptosymbol = forms.CharField(label='Buy Crypto Symbol', widget=forms.TextInput(attrs={'placeholder': 'Buy Crypto Symbol', 'id': 'buycryptosymbol-create'}), max_length=100 , required=False,)
    sellcryptosymbol = forms.CharField(label='Sell Crypto Symbol', widget=forms.TextInput(attrs={'placeholder': 'Sell Crypto Symbol', 'id': 'sellcryptosymbol-create'}), max_length=100 , required=False,)
    #currencytradingsymbol = forms.ChoiceField(label='Symbol', widget=CurrencyTradingWidget(), required=False,) 
    #cryptotradingsymbol = forms.CharField(label='Symbol', widget=CryptoTradingWidget(), max_length=30, required=False,) 
    quantity = forms.FloatField(label='Quantity', widget=forms.NumberInput(attrs={'placeholder': 'Quantity', 'id': 'quantity-create'}), required=False, localize=True)
    price = forms.FloatField(label='Price', widget=forms.NumberInput(attrs={'placeholder': 'Price', 'id': 'price-create'}), required=False, localize=True)
    proceed = forms.FloatField(label='Proceed', widget=forms.NumberInput(attrs={'placeholder': 'Proceed', 'id': 'proceed-create'}), localize=True)
    fee = forms.FloatField(label='Fee/Tax', widget=forms.NumberInput(attrs={'placeholder': 'Fee/tax deduction', 'id': 'fee-create'}), required=False, localize=True)
    basis = forms.FloatField(label='Basis', widget=forms.NumberInput(attrs={'placeholder': 'Basis', 'id': 'basis-create'}), required=True, localize=True)
    # basis = forms.FloatField(label='Basis', widget=CalculateBasis(), required=True,)
    remark = forms.CharField(label='Remark', widget=forms.TextInput(attrs={'placeholder': 'Remark', 'id': 'remark-create'}), max_length=300 , required=False,)


class EditTransaction(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['remark']
        widgets = {
            'remark': forms.TextInput(attrs={'placeholder': 'Remark', 'id': 'remark-edit'})
        }


""" Performance Filter form """
class PerformanceFilter(forms.Form):

    INTERVAL = [
        ('Weekly', 'Weekly'), 
        ('Monthly', 'Monthly'), 
        ('Yearly', 'Yearly'), 
    ]
    
    asset = forms.ChoiceField(label='Asset', widget=forms.Select(attrs={'id': 'asset-performance'}), choices=ASSETS, required=False,)
    interval = forms.ChoiceField(label='Interval', widget=forms.Select(attrs={'id': 'interval-performance'}), choices=INTERVAL, required=False,)

"""User authentication and creation"""
class Login(AuthenticationForm):
    class Meta:
        model = User
        fields = ('email', 'password')
    #email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'email', 'autofocus': True}), required=True)
    #password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password'}), required=True)


class Registration(UserCreationForm):
    #email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'email', 'autofocus': True}), required=True)
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')