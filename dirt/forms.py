from django import forms
import datetime
from .models import AllData, HDC_Data


class AllDataSurvey(forms.ModelForm):
    model=AllData
    errors = None
    fields = ('location')

class HdcDataSurvey(forms.ModelForm):
    model=HDC_Data
    errors = None
    fields = ('location')
