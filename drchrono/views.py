from social_django.models import UserSocialAuth
import datetime
import pytz

from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from .models import Doctor, Appointment, Patient
from .forms import CheckinForm
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint
import utils

class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    Get today's appointments and store appointments and patients in database.
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_doctor_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)

        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        doctor = next(api.list())

        # Add doctor to local database if does not exist yet and return doctor obj
        return Doctor.objects.add_doctor(doctor)

    def make_patient_request(self):
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        patients = list(api.list())
        
        # Add patient to local database if does not exist yet
        for patient in patients:
            Patient.objects.add_patient(patient)

    def make_appointment_request(self):
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        
        # Converting date into DD-MM-YYYY format
        date = datetime.datetime.today()
        current_date = (date.strftime('%Y-%m-%d'))

        appointments_from_api = list(api.list({}, current_date))

        # Add appointment to local database if does not exist yet
        for appointment in appointments_from_api:
           Appointment.objects.add_appointment(appointment)

        status_query = self.request.GET.get('query')

        # Retrieve appointments from local database with query filter
        appointments = Appointment.objects.get_todays_appointments(date, status_query)
        return appointments

    def post(self, request):
        id = request.POST.get('appointment')
        status = request.POST.get('status')
        if status == 'Checked In':
            appointment_obj, created = Appointment.objects.update_or_create(
                pk=id,
                defaults={
                'status': status,
                'time_checkedin': datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                },
            )
            return redirect('arrived')
        elif status == 'In Session':
            appointment = Appointment.objects.get(pk=id)
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            time_patient_waited = round((now - appointment.time_checkedin).total_seconds()/60)
            appointment_obj, created = Appointment.objects.update_or_create(
                pk=id,
                defaults={
                'status': status,
                'time_doctor_started': now,
                'time_patient_waited': time_patient_waited,
                },
            )
            return redirect('setup')
        elif status == 'Complete':
            appointment_obj, created = Appointment.objects.update_or_create(
                pk=id,
                defaults={
                'status': status,
                'time_doctor_completed': datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
                },
            )
            return redirect('setup')
        elif status == '':
            appointment_obj, created = Appointment.objects.update_or_create(
                pk=id,
                defaults={
                'status': status,
                 'time_checkedin':None,
                'time_doctor_started': None,
                'time_doctor_completed': None,
                },
            )
            return redirect('setup')

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        doctor_details = self.make_doctor_request()
        self.make_patient_request()
        appointments_details = self.make_appointment_request()
        avg_wait_time_today = utils.get_avg_wait_time_today(appointments_details)
        kwargs['doctor'] = doctor_details
        kwargs['appointments'] = appointments_details
        kwargs['avg_wait_time_today'] = avg_wait_time_today
        return kwargs

class Arrived(TemplateView):
    """
    Shows successful checkin page
    """
    template_name = 'arrived.html'

class History(TemplateView):
    """
    Shows data on past appointments
    """
    template_name = 'history.html'

    def get_context_data(self, **kwargs):
        kwargs = super(History, self).get_context_data(**kwargs)
        history_data = Appointment.objects.get_avg_wait_time_all()
        kwargs['avg_wait_time_all'] = history_data['avg_wait']
        kwargs['total_apps_count'] = history_data['total_apps_count']
        return kwargs

class Checkin(TemplateView):
    form_class = CheckinForm
    template_name = 'checkin.html'

    def post(self, request):
        form = CheckinForm(request.POST or None)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            # social_security_number = form.cleaned_data.get('social_security_number')

            patient_lookup = Patient.objects.lookup_patient(first_name, last_name)
            # Display errors if did not find patient info or appointments for today
            if not patient_lookup:
                return render(request, self.template_name, {
                    'form': form,
                    "message": "No matching patient information found, "
                    "please check first/last name and SSN again!"
                })

            today = datetime.datetime.today()
            appointment_lookup = Appointment.objects.lookup_appointment(patient_lookup, today)

            if not appointment_lookup:
                return render(request, self.template_name, {
                    'form': form,
                    "message": "No appointments scheduled for this patient today!"
                })

            # Display matched appointments for patient today
            return render(request, 'appointments.html', {'appointments': appointment_lookup})
    
    def get_context_data(self, **kwargs):
        kwargs = super(Checkin, self).get_context_data(**kwargs)
        form = self.form_class
        kwargs['form']= form
        return kwargs