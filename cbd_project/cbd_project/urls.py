from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from cbd import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^save_coding/$', views.save_coding, name='save_coding'),
    url(r'^moderate/$', views.moderate, name='moderate'),
    url(r'^logout/$',  views.user_logout, name='logout'),
]
