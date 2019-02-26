from django import forms
from django.forms import widgets
from django.core.validators import RegexValidator

class CheckinForm(forms.Form):
  first_name = forms.CharField(label='First Name', max_length=100)
  last_name = forms.CharField(label='Last Name', max_length=100)
  social_security_number = forms.CharField(
    required=False,
    label='Social Secuirty Number',
    max_length=15,
    validators=[
      RegexValidator('^(?!000|.+0{4})(?:\d{3}-\d{2}-\d{4})$', 
      message="SSN is optional. If entered, enter it in XXX-XX-XXXX format")
    ]
  )

  def clean_first_name(self):
    first_name_passed = self.cleaned_data.get('first_name')
    if first_name_passed.strip() == '':
      raise forms.ValidationError('Please provide first name')
    return first_name_passed

  def clean_last_name(self):
    last_name_passed = self.cleaned_data.get('last_name')
    if last_name_passed.strip() == '':
      raise forms.ValidationError('Please provide last name')
    return last_name_passed