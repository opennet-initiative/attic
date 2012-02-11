from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from oni_manager_app import views
from django.conf.urls.defaults import *
from django.views.generic import list_detail
from oni_manager_app.models import Mitglied 
from django.contrib.auth.decorators import login_required

member_detail_info = {
    'queryset': Mitglied.objects.all(),
    'template_name': 'members/all_members.html',
}

urlpatterns = patterns('',
    # Examples:
    url(r'^login/$', 'django.contrib.auth.views.login'),
    # url(r'^oni_manager/', include('oni_manager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^signup/', views.signup),
    url(r'^logout', views.logout_view),
    url(r'^register/', views.register),
    
    (r'^members/$', login_required(list_detail.object_list), member_detail_info),
    (r'^members/(?P<member_id>\d+)/$', views.viewMember),
    
    url('', views.home_view)
    
)
