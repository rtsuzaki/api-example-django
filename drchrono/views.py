from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth
import datetime

from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint
from .models import Doctor, Appointment, Patient
from .forms import CheckinForm
from django.shortcuts import render, redirect
import helpers

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
        doctor_obj, created = Doctor.objects.get_or_create(pk=doctor['id'])
        return doctor

    def make_patient_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        
        patients = list(api.list())
        
        for patient in patients:
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
        return patients

    def make_appointment_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        
        d = datetime.datetime.today()
        
        # Converting date into DD-MM-YYYY format
        current_date = (d.strftime('%Y-%m-%d'))
        
        appointments_from_api = list(api.list({}, current_date))
        for appointment in appointments_from_api:
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
                },
            )

        appointments = helpers.get_todays_appointments()
        return appointments

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_doctor_request()
        patient_details = self.make_patient_request()
        appointments_details = self.make_appointment_request()

        kwargs['doctor'] = doctor_details
        kwargs['appointments'] = appointments_details
        kwargs['patients'] = patient_details
        return kwargs

# class Appointments(TemplateView):
#     """
#     The doctor can see what appointments they have today.
#     """
#     template_name = 'appointments.html'

#     def get_token(self):
#         """
#         Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
#         already signed in.
#         """
#         oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
#         access_token = oauth_provider.extra_data['access_token']
#         return access_token

#     def make_api_request(self):
#         """
#         Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
#         proved that the OAuth setup is working
#         """
#         # We can create an instance of an endpoint resource class, and use it to fetch details
#         access_token = self.get_token()
#         api = AppointmentEndpoint(access_token)
#         # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
#         # account probably only has one doctor in it.
        
#         d = datetime.datetime.today()
        
#         # Converting date into DD-MM-YYYY format
#         current_date = (d.strftime('%Y-%m-%d'))
#         return api.list({}, current_date)

#     def get_context_data(self, **kwargs):
#         kwargs = super(Appointments, self).get_context_data(**kwargs)
#         # Hit the API using one of the endpoints just to prove that we can
#         # If this works, then your oAuth setup is working correctly.
#         appointments_details = self.make_api_request()
#         kwargs['appointments'] = appointments_details
#         return kwargs

# class Checkin(TemplateView):
#     template_name = 'checkin.html'

#     def checkin_patient(request):
#         if request.method == 'POST':
#             form = CheckinForm(request.POST or None)
#             if form.is_valid():
#                 first_name = form.cleaned_data.get('first_name')
#                 last_name = form.cleaned_data.get('last_name')
#                 return 'Success'

#     def get_context_data(self, **kwargs):
#         kwargs = super(Checkin, self).get_context_data(**kwargs)
#         # Hit the API using one of the endpoints just to prove that we can
#         # If this works, then your oAuth setup is working correctly.
#         message = self.checkin_patient('POST')
#         kwargs['message'] = message
#         return kwargs

def checkin_patient(request):
    form = CheckinForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            # social_security_number = form.cleaned_data.get('social_security_number')

            lookup_patient = helpers.lookup_patient(first_name, last_name)
            # Display errors if did not find patient info or appointments for today
            if not lookup_patient:
                return render(request, "checkin.html", {
                    'form': form,
                    "message": "No patient information found, "
                    "please check first/last name and SSN again!"
                })

            lookup_appointment = helpers.lookup_appointment(lookup_patient)
            if not lookup_appointment:
                return render(request, "checkin.html", {
                    'form': form,
                    "message": "No appointments scheduled for this patient today!"
                })

            # Display matched appointments for patient today
            return render(request, 'appointments.html', {'appointments': lookup_appointment})

    return render(request, 'checkin.html', {'form': form})

def update_app_status(request):
    if (request.method == 'POST'):
        # appointment = lookup_appointment_by_id(request.POST.get('appointment'))
        id = request.POST.get('appointment')
        status = request.POST.get('status')
        print(status)
        appointment_obj, created = Appointment.objects.update_or_create(
            pk=id,
            defaults={
            'status': status,
            },
        )
        if status == 'Checked In':
            return redirect('arrived')
        else:
            return redirect('setup')

    return render(request, 'checkin.html')

class Arrived(TemplateView):
    """
    Shows successful checkin page
    """
    template_name = 'arrived.html'