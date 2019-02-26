from models import Patient, Appointment
from django.utils.timesince import timesince
from django.db.models import Q
import datetime
import pytz

def lookup_patient(first_name, last_name):
  if not Patient.objects.filter(
      # doctor=doctor,
      first_name=first_name,
      last_name=last_name).exists():
      # social_security_number=social_security_number).exists():
    return None

  return Patient.objects.get(
    # doctor=doctor,
    first_name=first_name,
    last_name=last_name)
    # social_security_number=ssn)

def lookup_appointment(patient):
  d = datetime.datetime.today()
  appointments = Appointment.objects.filter(
    patient=patient,
    status='',
    scheduled_time__year=d.year,
    scheduled_time__month=d.month,
    scheduled_time__day=d.day
  ).order_by('scheduled_time')
  
  return appointments

def lookup_appointment_by_id(id):
  return Appointment.objects.filter(id=id)

def get_todays_appointments(today):
  appointments = Appointment.objects.filter(
    scheduled_time__year=today.year,
    scheduled_time__month=today.month,
    scheduled_time__day=today.day
  ).order_by('scheduled_time')
  return appointments

def get_avg_wait_time_today(appointments):
  count = 0
  time = datetime.timedelta(minutes=0)
  now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
  for appointment in appointments:
    count += 1
    time_checkedin = appointment.time_checkedin
    time_doctor_started = appointment.time_doctor_started
    if appointment.status == 'Checked In':
      time += now - time_checkedin
    if appointment.status == 'Complete' or appointment.status == 'In Session':
      time += time_doctor_started - time_checkedin
  if (count == 0):
    return 0
  else:
    # Calculate average appointment time in minutes, rounded to nearest minute
    return round(time.total_seconds()/60/count)
  
      
def get_avg_wait_time_all():
  appointments = Appointment.objects.filter(
    Q(status='In Session') | Q(status='Completed')
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