# forms.py
from django import forms

class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', required=False)

