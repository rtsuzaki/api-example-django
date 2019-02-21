from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
# from django.contrib.auth import views as auth_views
admin.autodiscover()
import views


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    # url(r'^appointments/$', views.Appointments.as_view(), name='kiosk'),
    url(r'^checkin/$', views.checkin_patient, name='checkin'),
    url(r'^selected/$', views.select_app, name='select_app'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]