from django import forms
from django.forms.widgets import CheckboxInput


class TrainingModelForm(forms.Form):

    dataSetFile = forms.FileField()

    DT = forms.BooleanField(initial=False, required=False, widget=CheckboxInput(
        attrs={
        'class': 'form-check-input'
        }
    ))

    RFC = forms.BooleanField(initial=False, required=False, widget=CheckboxInput(
        attrs={
        'class': 'form-check-input'
        }
    ))

    min_depth = forms.IntegerField()

    max_depth = forms.IntegerField()