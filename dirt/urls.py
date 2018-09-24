from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from django.urls import path, re_path
from  dirt import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    re_path(r'^beach_litter.html', views.beach_litter, name='beach-litter-home'),
    re_path(r'^california.html', views.litter_california, name='california'),
    # re_path(r'^litter/california/(?P<location>[-\w+]+[-\w+])/$', views.cali_search, name='california-search'),
    re_path(r'^litter/city/(?P<city>[-\w+]+[-\w+])/$', views.litter_city, name='city-search'),
    re_path(r'^litter/lake-river/(?P<lakeRiver>[-\w+]+[-\w+])/$', views.litter_water, name='lakeRiver-search'),
    re_path(r'^litter/location/(?P<location>[-\w+]+[-\w+])/$', views.litter_location, name='location-search'),
    re_path(r'^litter/project/(?P<project>[-\w+]+[-\w+])/$', views.litter_project, name='project-search'),
    re_path(r'^microbiology.html', views.microbiology, name='micro'),
    re_path(r'^$', views.index, name='home'),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api-token-auth/', obtain_jwt_token),
    re_path(r'hd_api^$', views.api_root),
    re_path(r'^create-record/', views.CreateRecord.as_view(), name='create-record'),
    re_path(r'^codes/(?P<location>[-\w+ ]+[-\w+])/$', views.LitterApi.as_view(), name='location'),
    re_path(r'^codes/(?P<location>[-\w+ ]+[-\w+])/(?P<code>[-\w]+)/$', views.LitterApiCode.as_view(), name='location-code'),
    re_path(r'^create-beach/', views.CreateBeach.as_view(), name='create-beach'),
    re_path(r'^beaches/(?P<name>[-\w+ ]+[-\w+])/$', views.BeachApi.as_view(), name='beaches'),
    re_path(r'^city-list/', views.CityList.as_view(), name='city-list'),
    re_path(r'^summary/(?P<water>[-\w+ ]+[-\w+])/$', views.LocationSummary.as_view(), name='location-summary'),
    re_path(r'^daily-total/(?P<location>[-\w+ ]+[-\w+])/$', views.DailyTotals.as_view(), name='daily-total'),

]
