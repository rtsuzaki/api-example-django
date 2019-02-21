from django.db import models

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


