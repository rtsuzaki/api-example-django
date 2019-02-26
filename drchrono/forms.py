from django import forms
from django.forms import widgets

class CheckinForm(forms.Form):
  first_name = forms.CharField(label='First Name', max_length=100)
  last_name = forms.CharField(label='Last Name', max_length=100)
  # social_security_number = forms.CharField(label='Social Secuirty Number', max_length=15)

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

  # def clean_social_security_number(self):
  #   social_security_number_passed = self.cleaned_data.get('social_security_number')
  #   if social_security_number_passed.strip() == '':
  #     raise forms.ValidationError('Please provide social security number')
  #   if len(social_security_number_passed.strip()) != 11:
  #     raise forms.ValidationError('Please enter SSN in the following format: XXX-XX-XXXX')