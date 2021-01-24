from django import forms
# from django.forms import Form, ModelForm
from .models import *



class addProductForm(forms.ModelForm):
    class Meta:
        model = products
        fields = '__all__'

class updateProductForm(forms.ModelForm):
    class Meta:
        model = products
        fields = '__all__'


class addSalesForm(forms.ModelForm):
    class Meta:
        model = sales
        fields = ['customer_name','physical_address', 'postal_address', 'customer_TIN', 'customer_VRN']

        labels = {
            'TIN Number': 'customer_TIN',
            'VRN Number': 'customer_VRN',
        }


class addPurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'quantity','total_price', 'date']

        widgets = {
            'date': forms.DateInput(attrs = {'type': 'date'})
        }


class addDepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['first_date', 'last_date']

        widgets = {
            'first_date': forms.DateInput(attrs = {'type': 'date'}),
            'last_date': forms.DateInput(attrs = {'type': 'date'})
        }


class addExpensesForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['expense', 'description', 'date', 'amount']

        widgets = {
            'date': forms.DateInput(attrs = {'type': 'date'})
        }

class addPercentageForm(forms.ModelForm):
    class Meta:
        model = Percentages
        fields = ['name', 'percent']
