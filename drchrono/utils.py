import datetime
import pytz

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