from models import Patient, Appointment
import datetime

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
  # current_date = (d.strftime('%Y-%m-%d'))

  appointments = Appointment.objects.filter(
    patient=patient,
    status='',
    scheduled_time__year=d.year,
    scheduled_time__month=d.month,
    scheduled_time__day=d.day
  ).order_by('scheduled_time')
  
  return appointments

