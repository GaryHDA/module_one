from django.conf.urls import url
from django.views.decorators.cache import cache_page


from  dirt import views

urlpatterns = [
# url(r'^$', views.index, name='index'),
url(r'^$', views.index, name='index'),
url(r'^search_MCBP/$', views.search_MCBP, name='MCBP_search_results'),
url(r'^search_hdc/$', views.search_hdc, name='MCBP_search_results'),
url(r'^search_SLR/$', views.search_SLR, name='SLR_search_results'),
url(r'^search_city/$', views.search_city, name='city_search_results'),
url(r'^search_water/$', views.search_water, name='water_search_results'),
url(r'^mcbp.html', views.mcbp_home, name='mcbp_home'),
url(r'^hdc.html', views.hdc_home, name='hdc_home'),
url(r'^slr.html', views.slr_home, name='slr_home'),
url(r'^beach_litter.html', views.beach_litter, name='litter_home'),
url(r'^services.html', views.services_home, name='services'),
url(r'^intheworks.html', views.in_the_works, name='in_the_works'),
url(r'^microbiology.html', views.microbiology, name='microbiology'),


]
