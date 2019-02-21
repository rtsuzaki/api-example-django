from django.db import models
from django.utils.timesince import timesince
import datetime
import pytz

# Add your models here
class Doctor(models.Model):
  id = models.IntegerField(primary_key=True)

class Patient(models.Model):
  id = models.IntegerField(primary_key=True)
  doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
  social_security_number = models.CharField(max_length=15)
  email = models.EmailField(max_length=50)

class Appointment(models.Model):
  id = models.IntegerField(primary_key=True)
  patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
  doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
  status = models.CharField(max_length=20, null=True)
  notes = models.CharField(max_length=200, blank=True)
  exam_room = models.IntegerField(blank=True, null=True)
  scheduled_time = models.DateTimeField(auto_now=False, auto_now_add=False)
  updated_at = models.DateTimeField(auto_now=True)
  duration = models.IntegerField(blank=True, null=True)
  time_checkedin = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
  time_doctor_started = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
  time_doctor_completed = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
  time_patient_waited = models.IntegerField(blank=True, null=True)

  def get_time_waiting(self):
    checkedin = self.time_checkedin
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return timesince(checkedin, now)

