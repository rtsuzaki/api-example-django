from django.db import models
from django.utils.timesince import timesince
import datetime
import pytz

class DoctorManager(models.Manager):
  def add_doctor(self, doctor):
    doctor_obj, created = Doctor.objects.get_or_create(
      pk=doctor['id'],
      defaults={
          'first_name': doctor['first_name'],
          'last_name': doctor['last_name'],
      },
    )
    return doctor_obj

class Doctor(models.Model):
  id = models.IntegerField(primary_key=True)
  first_name = models.CharField(max_length=100, null=True)
  last_name = models.CharField(max_length=100, null=True)

  objects = DoctorManager()

class PatientManager(models.Manager):
  def add_patient(self, patient):
    patient_obj, created = Patient.objects.get_or_create(
      pk=patient['id'],
      defaults={
          'doctor': Doctor.objects.get(pk=patient['doctor']),
          'first_name': patient['first_name'],
          'last_name': patient['last_name'],
          'social_security_number': patient['social_security_number'],
          'email': patient['email'],
      },
    )

  def lookup_patient(self, first_name, last_name):
    if not Patient.objects.filter(
      # doctor=doctor,
      first_name=first_name,
      last_name=last_name,
    ).exists():
      # social_security_number=social_security_number).exists():
      return None

    return Patient.objects.get(
      # doctor=doctor,
      first_name=first_name,
      last_name=last_name
    )
      # social_security_number=ssn)
  
class Patient(models.Model):
  id = models.IntegerField(primary_key=True)
  doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
  social_security_number = models.CharField(max_length=15)
  email = models.EmailField(max_length=50)

  objects = PatientManager()

class AppointmentManager(models.Manager):
  def add_appointment(self, appointment):
    appointment_obj, created = Appointment.objects.get_or_create(
      pk=appointment['id'],
      defaults={
          'patient':Patient.objects.get(pk=appointment['patient']),
          'doctor':Doctor.objects.get(pk=appointment['doctor']),
          'notes':appointment['notes'],
          'status':appointment['status'],
          'exam_room':appointment['exam_room'],
          'scheduled_time':appointment['scheduled_time'],
          'updated_at':appointment['updated_at'],
          'duration':appointment['duration'],
          'time_checkedin': None,
          'time_doctor_started': None,
          'time_doctor_completed': None,
      },
    )

  def lookup_appointment(self, patient, day):
    appointments = Appointment.objects.filter(
      patient=patient,
      status='',
      scheduled_time__year=day.year,
      scheduled_time__month=day.month,
      scheduled_time__day=day.day
    ).order_by('scheduled_time')
    return appointments
  
  def get_todays_appointments(self, today, status):
    appointments = Appointment.objects.filter(
      scheduled_time__year=today.year,
      scheduled_time__month=today.month,
      scheduled_time__day=today.day,
    ).order_by('scheduled_time')

    if status == None:
      return appointments
    elif status == 'seen':
      appointments = appointments.filter(
        models.Q(status='In Session') | models.Q(status='Completed'),
      ).order_by('scheduled_time')
      return appointments
    elif status == 'unseen':
      appointments = appointments.filter(
        models.Q(status='') | models.Q(status='Checked In'),
      ).order_by('scheduled_time')
      return appointments
  
  def get_avg_wait_time_all(self):
    appointments = Appointment.objects.filter(
      models.Q(status='In Session') | models.Q(status='Completed')
    )
    time = datetime.timedelta(minutes=0)
    if len(appointments) == 0:
      return {'avg_wait': 0, 'total_apps_count': 0}

    for appointment in appointments:
      time += appointment.time_doctor_started - appointment.time_checkedin
      
    avg_wait_time_all = round(time.total_seconds()/60/len(appointments))
    
    history_data = {
      'avg_wait': avg_wait_time_all,
      'total_apps_count': len(appointments),
    }
    return history_data

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

  objects = AppointmentManager()

  def get_time_waiting(self):
    checkedin = self.time_checkedin
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return timesince(checkedin, now)

