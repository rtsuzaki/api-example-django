from django import forms
from django.forms import widgets

# Add your forms here
class CheckinForm(forms.Form):
  first_name = forms.CharField(label='First Name', max_length=100)
  last_name = forms.CharField(label='Last Name', max_length=100)
  # social_security_number = forms.RegexField(

  # )
  def clean_first_name(self):
    first_name_passed = self.cleaned_data.get("first_name_passed")
    if first_name_passed.strip() == '':
      raise forms.ValidationError("Please provide first name")
    return first_name_passed

  def clean_last_name(self):
    last_name_passed = self.cleaned_data.get("last_name_passed")
    if last_name_passed.strip() == '':
      raise forms.ValidationError("Please provide last name")
    return last_name_passed