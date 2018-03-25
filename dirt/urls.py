from django.conf.urls import url
from django.views.decorators.cache import cache_page


from  dirt import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^search_MCBP/$', views.search_MCBP, name='MCBP_search_results'),
url(r'^search_SLR/$', views.search_SLR, name='SLR_search_results'),
url(r'^mcbp.html', views.mcbp_home, name='mcbp_home'),
url(r'^slr.html', views.slr_home, name='slr_home'),
url(r'^beach_litter.html', cache_page(10)(views.beach_litter), name='litter_home'),
url(r'^services.html', views.services_home, name='services'),
# url(r'^pension.html', views.finance_home, name='pension'),

]
