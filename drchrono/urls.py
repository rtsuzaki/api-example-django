from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
# from django.contrib.auth import views as auth_views
admin.autodiscover()
import views

urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^checkin/$', views.Checkin.as_view(), name='checkin'),
    url(r'^arrived/$', views.Arrived.as_view(), name='arrived'),
    url(r'^history/$', views.History.as_view(), name='history'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]