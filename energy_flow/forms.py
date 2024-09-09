from django import forms
from .models import GeneralSettings

class GeneralSettingsForm(forms.ModelForm):
    class Meta:
        model = GeneralSettings
        fields = '__all__'