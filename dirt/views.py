# django imprts
from django.shortcuts import render
from django.db.models import Sum, Avg, FloatField, F
from django.db.models.functions import Cast
from django.http import Http404
from django.conf import settings

# model imports from
from dirt.models import AllData, Beaches, HDC_Beaches, HDC_Data, PlatformActivity, References, Sponsors, LastCommit

# python imports
from statistics import mean
import datetime
from datetime import datetime
import numpy as np
from scipy.stats import norm
import os, json

# These are the functions that shape the data for various views
def item_data():
    """
    Initial query of all item counts
    """
    return AllData.objects.all()
def location_filter(q,l):
    """
    Returns all the data for a location in the given query.
    """
    return q.filter(location=l)
def project_filter(q,p):
    """
    Returns all the data for a project in the ItemData db.
    """
    return q.filter(location__project=p)
def water_filter(q,w):
    """
    Returns all the data for a body of water in the ItemData db.
    """
    return q.filter(location__water_name=w)
def city_filter(q,c):
    """
    Returns all the data for a body of water in the ItemData db.
    """
    return q.filter(location__city=c)
def city_list(q):
    """
    Returns a list of cities from a querry
    """
    return q.values_list('location__city', flat=True).distinct().order_by('location__city')
def project_list(q):
    """
    Returns a list of projects from a querry
    """
    return q.values_list('location__project', flat=True).distinct()
def location_list(q):
    """
    Returns a list of locations from a querry
    """
    return q.values_list('location', flat=True).distinct()
def water_list(q):
    """
    Returns a list of water bodies from a querry
    """
    return q.values_list('location__water_name', flat=True).distinct()
def list_of_lakes(q):
    """
    Returns a list of lakes in queryset
    """
    return q.filter(location__water='l').distinct().values_list('location__water_name', flat=True)
def list_of_rivers(q):
    """
    Returns a list of rivers in a queryset
    """
    return q.filter(location__water='r').distinct().values_list('location__water_name', flat=True)
def water_body_dict(q):
    """
    Returns a dicitionary {lake or river name: [list of locations on lake or river]}
    Takes a query and a list of river or lake names
    """
    b = list(q.values('location__water_name', 'location').distinct())
    c = {s['location__water_name']:[] for s in b}
    for d in b:
        c[d['location__water_name']].append(d['location'])
    return c
def location_total(q):
    """
    Returns the total of the quantity field.
    Acceppts a query set as an argument
    """
    return q.aggregate(total=Sum('quantity'))
def daily_total(q):
    """
    Returns the daily total by date for a queryset.
    tuple ('location', 'date', 'total')
    """
    return q.values('date').annotate(total=Sum('quantity')).values_list('location', 'date', 'length', 'total')
def daily_pcs_m(q):
    """
    Groups a query by location and date, divides qty by length
    Returns an array of arrays [['location', 'date', 'pcs/m']...['location', 'date', 'pcs/m']]
    """
    a = q.values('date', 'location').annotate(pcs_m = Sum(Cast(F('quantity'), FloatField()) / Cast(F('length'), FloatField())))
    b = list(a.values_list('location','date','pcs_m'))
    b = [[c[0], c[1], c[2]] for c in b]
    return b
def pcs_m_tup(a,l):
    """
    Takes the results from daily_pcs_m and returns a tuple ('location',[array of pcs/m])
    """
    b = [c[2] for c in a]
    return (l,b)
def beaches_in_a_region(a,l):
    """
    Returns the name, number of samples and avg pcs/m for locations
    in query. C is equal to a list of location names,
    """
    b = {x:[] for x in l}
    for y in a:
        b[y[0]].append(y[2])
    c = [(d, len(b[d]), round(mean(b[d]), 4)) for d in l]
    return c
def map_info(l,t,q):
    """
    Returns lat, on, city and project name from the Beaches tables
    accepts a list of location names and list of tuples from beaches in a region
    """
    # a = Beaches.objects.all()
    b = q.filter(location__in=l)
    c = b.values_list('location','latitude', 'longitude', 'city', 'project')
    d = {x[0]:(x[1],x[2], x[3],x[4]) for x in c}
    e = [a + d[a[0]] for a in t]
    f = [[x[0], x[1], x[2], float(x[3]), float(x[4]), x[5], x[6]] for x in e]
    return f
def pcs_m_y(d1, d2, values, query):
    """
    Returns an array of arrays [['location', 'date', 'pcs/m']...['location', 'date', 'pcs/m']]
    between two dates and limited to the locations in the query
    Accepts the results of daily_pcs_m
    """
    l = list(location_list(query))
    a = [x for x in values if x[0] in l]
    b = [[x[0], x[1].strftime("%Y-%m-%d"), x[2]] for x in a if x[1] >= datetime.strptime(d1, "%Y-%m-%d").date() and x[1] <datetime.strptime(d2, "%Y-%m-%d").date()]
    return b
def log_dist(a):
    """
    Returns an array of arrays [[x, norm.pdf(x)]...[x, norm.pdf(x)]]
    where the values of x is the log of the 2nd value in the argument array
    accepts output from pcs_m_y()
    """
    e_v = sorted([round(np.log(x[2]), 5) for x in a])
    e_m = round(np.mean(e_v), 5)
    e_dev = round(np.std(e_v), 5)
    e_x_y = [[x, round(norm.pdf(x,e_m, e_dev), 5)] for x in e_v]
    return e_x_y
def avg_pcs_m(t):
    """
    Returns the average of the array in pcs_m_tup
    """
    return (t[0], round(mean(t[1]),4))
def max_pcs_m(t):
    """
    Returns the max value  of the array in pcs_m_tup
    """
    a = (t[0], max(t[1]))
    return a
def min_pcs_m(t):
    """
    Returns the min value  of the array in pcs_m_tup
    """
    a = (t[0], min(t[1]))
    return a
def first_sample(q):
    """
    Returns the first sample date from a query set
    """
    return q.earliest('date').date
def last_sample(q):
    """
    Returns the last sample date froma a query set
    """
    return q.latest('date').date
def num_samples(t):
    """
    Returns the number of samples for a query set
    Uses len(value) from the pcs_m_tup
    """
    return (t[0], len(t[1]))
def twenty_fith(t):
    """
    Returns the 25th percentile from an array
    Accepts a tuple where the array is in the [1] position
    """
    #a = np.array(t[1])
    return np.percentile(t[1], 25)
def seventy_fifth(t):
    """
    Returns the 75th percentile from an array
    Accepts a tuple where the array is in the [1] position
    """
    # a = np.array(t[1])
    return np.percentile(t[1], 75)
def standard_dev(t):
    """
    Returns the standard deviation from an array
    Accepts a tuple where the array is in the [1] position
    """
    # a = np.array(t[1])
    return np.std(t[1])
def number_of_locations_region(q):
    """
    Returns the number of locations for a query set
    """
    return location_list(q).count()
def code_inventory(q,t):
    """
    Returns the total inventory and percent of total by code and quantity for a querySet
    d = the aggregated total of all objects in the queryset 'location_total(q)'
    """
    a = q.values('code').annotate(total=Sum('quantity')).annotate(percents= (Cast(F('total'), FloatField())/t)*100)
    b = a.values_list('code', 'code__description','code__material', 'total', 'percents').order_by('-total')
    return b
def material_inventory(q,t):
    """
    Returns the total inventory by material and quantity for a querySet
    """
    a = q.values('code__material').annotate(total=Sum('quantity')).annotate(percents= (Cast(F('total'), FloatField())/t)*100)
    b = a.values_list('code__material', 'total', 'percents').order_by('-total')
    return b
def code_t_ten(q):
    """
    Returns the top ten values from total inventory of MLW codes
    """
    a = q[:10]
    return a
def item_summary(q, l):
    """
    Returns the content of the summary table for any query
    """
    a = daily_pcs_m(q)
    b = pcs_m_tup(a, l)
    c = number_of_locations_region(q)
    d = location_total(q)['total']
    e = num_samples(b)[1]
    f = first_sample(q).strftime("%Y-%m")
    g = last_sample(q).strftime("%Y-%m")
    h = avg_pcs_m(b)[1]
    i = max_pcs_m(b)[1]
    j = min_pcs_m(b)[1]
    k = twenty_fith(b)
    x = seventy_fifth(b)
    m = list_of_lakes(q).count()
    n = list_of_rivers(q).count()
    o = standard_dev(b)
    p = l

    return [a, b], [c, d, e, f, g, h, i, j, k, x, m, n, o, p]
def item_data_exclude_locations(q, l):
    """
    Returns the daily values of all locations with the exception of the location(s)
    in the given list.
    Used for scatterplots putting a locaction/region in opposition of all other data
    """
    b = q.exclude(location__in=l)
    return b
def sponsors_volunteers(l):
    """
    Separates the data from the sponsors model.
    Returns two lists of lists one list holds sponsor data
    the other participant data
    """
    a = [b for b in l if b[4] == 's']
    c = [d for d in l if d[4] == 'm' or d[4] == 'v']
    return a, c
def lists_for_search_button(q):
    a = city_list(q)
    b = water_list(q)
    c = project_list(q)
    d = location_list(q)
    return a, b, c, d
# These are views for the app they use the functions above
def beach_litter(request):
    a = item_data()

    # fills the modal lake/river locations
    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))
    # gets the pcs-m, dailyt totals and summary values
    # fills the summary data table
    daily_values, summary = item_summary(a,'All locations')
    # fills the total inventory modal
    inventory = code_inventory(a, summary[1])
    # location names in this query
    all_locations = location_list(a)
    # these are for the data search button
    search_city, search_water, search_project, search_location = lists_for_search_button(a)
    # data for the topten and material modal
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    # fills the modal for locations and samples summary modal in a query
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    # data needed for the map output
    combined_map = map_info(all_locations, locations_samples, Beaches.objects.all())
    # time series data for scatter plot
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]
    # computing the scatter plots and distributions for the probability of garbage
    # this limits the locations to lac leman
    lac_leman = Beaches.objects.filter(water_name='Lac-Léman')
    # these gets the values from scatter_plot limits them to locations on lac Leman
    # and seperates them by year

    year_one = pcs_m_y('2015-11-15', '2016-11-15',  daily_values[0],lac_leman)
    year_two = pcs_m_y('2016-11-15', '2017-11-15',  daily_values[0], lac_leman)
    year_three = pcs_m_y('2017-11-15', '2018-11-15',  daily_values[0], lac_leman)
    # these make the distributions for the distribution plot
    dist_y_one = log_dist(year_one)
    dist_y_two = log_dist(year_two)
    y_one_s = len(dist_y_one)
    y_two_s = len(dist_y_two)

    # this gets the og_data for the header and participant data
    def og_data(l):
        a = list(Sponsors.objects.filter(beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
        return a

    # break that up into sponsors: people who paid for the service and those who rendered the service
    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    return render(request, 'dirt/beach_litter.html',  {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory,  'material_percents':material_percents,'code_top_ten':code_top_ten,'locations_samples':locations_samples,
    'all_locations':all_locations, 'scatter_plot':scatter_plot,'combined_map':combined_map, 'year_one':year_one, 'year_two':year_two,
    'year_three':year_three, 'dist_y_one':dist_y_one, 'dist_y_two':dist_y_two, 'y_one_s':y_one_s, 'y_two_s':y_two_s,  'sponsors':sponsors,
    'crew':crew, 'search_city': search_city, 'search_water':search_water, 'search_project':search_project, 'search_location':search_location})
def litter_city(request, city):

    x = city_list(item_data())
    if city in x:
        a = city_filter(item_data(),city)
        all_locations = location_list(a)
        other_data = item_data()
        beaches = Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a
    elif city in city_list(HDC_Data.objects.all()):
        a = city_filter(HDC_Data.objects.all(), city)
        all_locations = location_list(a)
        other_data = HDC_Data.objects.all()
        beaches = HDC_Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(ca_beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a

    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))
    daily_values, summary = item_summary(a,city)
    inventory = code_inventory(a, summary[1])
    all_locations = location_list(a)
    search_city, search_water, search_project, search_location = lists_for_search_button(other_data)
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    combined_map = map_info(all_locations, locations_samples, beaches)
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]
    other_scatter = daily_pcs_m(item_data_exclude_locations(other_data, all_locations))
    total_scatter = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in other_scatter]
    def see_that():
        a = ''.join(["http://mwshovel.pythonanywhere.com/dirt/litter/city","/",city,"/"])
        return a
    og_return_url = see_that()

    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    # def sponsor_image():
    #     sponsor = Sponsors.filter(city=city).values('sponsor')
    #     a = ''.join(["images/sponsors", sponsor['city']])


    return render(request, 'dirt/litter_search.html', {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory,  'material_percents':material_percents, 'code_top_ten':code_top_ten,'locations_samples':locations_samples,
    'all_locations':all_locations,'scatter_plot':scatter_plot, 'total_scatter':total_scatter, 'combined_map':combined_map, 'og_return_url':og_return_url,
    'sponsors':sponsors, 'crew':crew, 'search_city': search_city, 'search_water':search_water,'search_project':search_project, 'search_location':search_location})
def litter_water(request, lakeRiver):

    x = water_list(item_data())
    if lakeRiver in x:
        a = water_filter(item_data(), lakeRiver)
        all_locations = location_list(a)
        other_data = item_data()
        beaches = Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a
    elif lakeRiver in water_list(HDC_Data.objects.all()):
        a = water_filter(HDC_Data.objects.all(), lakeRiver)
        all_locations = location_list(a)
        other_data = HDC_Data.objects.all()
        beaches = HDC_Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(ca_beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a

    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))
    daily_values, summary = item_summary(a,lakeRiver)
    inventory = code_inventory(a, summary[1])
    all_locations = location_list(a)
    search_city, search_water, search_project, search_location = lists_for_search_button(other_data)
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    combined_map = map_info(all_locations, locations_samples, beaches)
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]
    other_scatter = daily_pcs_m(item_data_exclude_locations(other_data, all_locations))
    total_scatter = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in other_scatter]

    def see_that():
        a = ''.join(["http://mwshovel.pythonanywhere.com/dirt/litter/lake-river","/",lakeRiver,"/"])
        return a
    og_return_url = see_that()

    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    return render(request, 'dirt/litter_search.html', {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory,'material_percents':material_percents,'code_top_ten':code_top_ten,'locations_samples':locations_samples,
    'all_locations':all_locations, 'scatter_plot':scatter_plot, 'total_scatter':total_scatter, 'combined_map':combined_map, 'og_return_url':og_return_url,
    'sponsors':sponsors, 'crew':crew, 'search_city': search_city, 'search_water':search_water,'search_project':search_project, 'search_location':search_location})
def litter_project(request, project):

    if project in ['MCBP', 'SLR', 'PC', 'MWP']:
        a = project_filter(item_data(), project)
        all_locations = location_list(a)
        other_data = item_data()
        beaches = Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a
    elif project in ['HDC']:
        a = project_filter(HDC_Data.objects.all(), project)
        all_locations = location_list(a)
        other_data = HDC_Data.objects.all()
        beaches = HDC_Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(ca_beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a

    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))
    daily_values, summary = item_summary(a,project)
    inventory = code_inventory(a, summary[1])
    all_locations = location_list(a)
    search_city, search_water, search_project, search_location = lists_for_search_button(other_data)
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    combined_map = map_info(all_locations, locations_samples, beaches)
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]
    other_scatter = daily_pcs_m(item_data_exclude_locations(other_data, all_locations))
    total_scatter = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in other_scatter]

    def see_that():
        a = ''.join(["http://mwshovel.pythonanywhere.com/dirt/litter/project","/",project,"/"])
        return a
    og_return_url = see_that()

    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    return render(request, 'dirt/litter_search.html', {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory,'material_percents':material_percents,'code_top_ten':code_top_ten,'locations_samples':locations_samples, 'all_locations':all_locations,
    'scatter_plot':scatter_plot, 'total_scatter':total_scatter, 'combined_map':combined_map, 'og_return_url':og_return_url, 'sponsors':sponsors, 'crew':crew,
    'search_city': search_city, 'search_water':search_water,'search_project':search_project, 'search_location':search_location})
def litter_location(request, location):
    all_locations = location_list(item_data())

    if location in all_locations:
        a = location_filter(item_data(), location)
        all_locations = location_list(a)
        other_data = item_data()
        beaches = Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a
    elif location in location_list(HDC_Data.objects.all()):
        a = location_filter(HDC_Data.objects.all(), location)
        all_locations = location_list(a)
        other_data = HDC_Data.objects.all()
        beaches = HDC_Beaches.objects.all()
        def og_data(l):
            a = list(Sponsors.objects.filter(ca_beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff').distinct())
            return a

    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))
    daily_values, summary = item_summary(a,location)
    inventory = code_inventory(a, summary[1])
    #all_locations = location_list(a)
    search_city, search_water, search_project, search_location = lists_for_search_button(other_data)
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    combined_map = map_info(all_locations, locations_samples, beaches)
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]
    other_scatter = daily_pcs_m(item_data_exclude_locations(other_data, all_locations))
    total_scatter = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in other_scatter]

    def see_that():
        a = ''.join(["http://mwshovel.pythonanywhere.com/dirt/litter/location","/",location,"/"])
        return a
    og_return_url = see_that()

    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    return render(request, 'dirt/litter_search.html', {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory, 'material_percents':material_percents,'code_top_ten':code_top_ten,'locations_samples':locations_samples, 'all_locations':all_locations,
    'scatter_plot':scatter_plot, 'total_scatter':total_scatter, 'combined_map':combined_map, 'og_return_url':og_return_url, 'sponsors':sponsors, 'crew':crew,
    'search_city': search_city, 'search_water':search_water,'search_project':search_project, 'search_location':search_location})
def litter_california(request):
    a = HDC_Data.objects.all()
    lake_locations = water_body_dict(a.filter(location__water = 'l'))
    river_locations = water_body_dict(a.filter(location__water = 'r'))

    daily_values, summary = item_summary(a,'California')
    inventory = code_inventory(a, summary[1])
    all_locations = location_list(a)
    search_city, search_water, search_project, search_location = lists_for_search_button(a)
    material_percents = material_inventory(a, summary[1])
    code_top_ten = code_t_ten(inventory)
    locations_samples = beaches_in_a_region(daily_values[0], all_locations)
    combined_map = map_info(all_locations, locations_samples, HDC_Beaches.objects.all())
    scatter_plot = [[c[0], c[1].strftime("%Y-%m-%d"), c[2]] for c in daily_values[0]]

    # def see_that():
    #     a = ''.join(["http://127.0.0.1:8000/dirt/litter/city","/",city,"/"])
    #     return a
    # og_return_url = see_that()
    def og_data(l):
        a = list(Sponsors.objects.filter(ca_beach__location__in=l).values_list('sponsor', 'sponsor_icon_name', 'sponsor_url', 'message', 'is_staff' ).distinct())
        return a
    sponsor_data = og_data(all_locations)
    sponsors, crew = sponsors_volunteers(sponsor_data)

    return render(request, 'dirt/california.html', {'lake_locations':lake_locations, 'summary':summary,'river_locations':river_locations,
    'inventory':inventory, 'material_percents':material_percents,'code_top_ten':code_top_ten,'locations_samples':locations_samples, 'all_locations':all_locations,
    'scatter_plot':scatter_plot, 'combined_map':combined_map, 'sponsors':sponsors, 'crew':crew, 'search_city': search_city, 'search_water':search_water,
    'search_project':search_project, 'search_location':search_location})
def microbiology(request):

    def get_jsons_x(file_name):
        with open(os.path.join(settings.BASE_DIR, 'dirt/static/jsons/' + file_name ), 'r') as f:
            a = json.load(f)
            return a

    mrd_map = get_jsons_x('summ_mrd_map.json')
    t_cfu_17 = get_jsons_x('t_cfu_17.json')
    t_uv_17 = get_jsons_x('total_uv17.json')
    rain_17 = get_jsons_x('rain_17.json')
    rain_16 = get_jsons_x('rain_16.json')
    big_blue17 = get_jsons_x('big_blue17.json')
    big_blue16 = get_jsons_x('big_blue16.json')
    t_cfu_16 = get_jsons_x('t_cfu_16.json')
    sige_points = get_jsons_x('sige_points.json')
    # books = Make_library.books
    return render(request, 'dirt/microbiology.html', {'b_blue17_svt':big_blue17[2], 'b_blue17_vnx':big_blue17[1], 'b_blue17_mrd':big_blue17[0],
                'rain_17':rain_17, 'map_points':mrd_map, 't_cfu_17_mrd':t_cfu_17[0], 't_cfu_17_vnx': t_cfu_17[1],
                't_cfu_17_svt': t_cfu_17[2], 't_uv_17_svt':t_uv_17[2], 't_uv_17_mrd':t_uv_17[0], 't_uv_17_vnx':t_uv_17[1],
                'b_blue16_svt':big_blue16[2], 'b_blue16_vnx':big_blue16[1], 'b_blue16_mrd':big_blue16[0], 't_cfu_16_mrd':t_cfu_16[0], 't_cfu_16_vnx': t_cfu_16[1],
                't_cfu_16_svt': t_cfu_16[2], 'rain_16':rain_16, 'sige_points':sige_points})
def index(request):
    def last_litter_activity():
        a = item_data()
        b = last_sample(a)
        e = a.filter(date=b).values('location').annotate(total=Sum('quantity')).values_list('date', 'location', 'location__city', 'total')
        d = [[c[1], c[0].strftime("%Y-%m-%d"), c[2], c[3]] for c in e]
        return d
    latest_sample = last_litter_activity()
    def see_that():
        a = ''.join(["http://127.0.0.1:8000/dirt/litter/location","/",latest_sample[0][0],"/"])
        return a
    see_latest = see_that()
    print(latest_sample[0][0])
    def last_post():
        a = PlatformActivity.objects.values_list('date','platform', 'subject', 'comments', 'ur_l', 'owner').latest()
        b = [a[1], a[0].strftime("%Y-%m-%d"), a[2], a[3], a[4], a[5]]
        return b
    def last_read():
        a = References.objects.values_list('title','author', 'subject', 'abstract').latest()
        b = [a[0], a[1], a[2], a[3]]
        return b
    def last_commit():
        a = LastCommit.objects.values_list('date','repo', 'comments', 'ur_l').latest()
        b = [a[0].strftime("%Y-%m-%d"), a[1], a[2], a[3]]
        return b


    return render(request, 'dirt/index.html',{'latest_sample':latest_sample, "see_latest":see_latest, 'last_post':last_post(),
                  'last_read':last_read(), 'last_commit':last_commit()})
def code_shovel(request):
    return render(request, 'dirt/code-shovel.html')
def probability_view(request):
    return render(request, 'dirt/probability.html')
def about_hd(request):
    return render(request, 'dirt/About.html')
def sponsor_program(request):
    return render(request, 'dirt/sponsorship.html')


# imports specific to the API
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from dirt.serializers import SummarySerializer, MakeJson, AllDataSerial, BeachSerial, AllDataCreate, CitySerializer, AllDataSerial, BeachCreate, DailyTotalSerial, DailyLogSerial, HdcDataCreate, HdcBeachCreate
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import permissions, reverse
from django.http import Http404
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_jwt.views import obtain_jwt_token

# API views
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'all-objects': reverse('location', request=request, format=format),
        'one-object': reverse('location-code', request=request, format=format),
        'beach': reverse('beaches', request=request, format=format),
        'city-list': reverse('city-list', request=request, format=format),
        'summaries': reverse('location-summary', request=request, format=format),
        'daily-density': reverse('daily-dens', request=request, format=format),
        'api_home.html': reverse('api-home', request=request, format=format),
    })
def api_home(request):
     return render(request,'api-home.html')
class CreateRecord(generics.CreateAPIView):
    '''
    The is the data-entry api for hammerdirt beach litter surveys.  Enter a record for each object identified.

       1) A login is required

       2) The beach location and project must exist

           a) Go to 'hammerdirt/create-beach/' if need be

           b) The project must exist, contat roger@hammerdirt to get a project started

           c) Login required

    contact roger@hammerdirt.ch for login information

    '''
    queryset = AllData.objects.all()
    serializer_class = AllDataCreate
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
class CaCreateRecord(generics.CreateAPIView):
    '''
    The is the data-entry api for hammerdirt beach litter surveys.  Enter a record for each object identified.

       1) A login is required

       2) The beach location and project must exist

           a) Go to 'hammerdirt/create-beach/' if need be

           b) The project must exist, contat roger@hammerdirt to get a project started

           c) Login required

    contact roger@hammerdirt.ch for login information

    '''
    queryset = HDC_Data.objects.all()
    serializer_class = HdcDataCreate
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
class LitterApi(APIView):
    """
    This is the searchable api for hammerdirt beachlitter records. Get all the records for a city, lake/river, project or location.
    The search can be further refined to the object level.  For example to get all the surveys where the G95 code was indentified in Vevey:

         enter: 'hammerdirt/codes/Vevey/G95/

    Valid terms are City, Body of water, Project name, Survey location name. To get all the data for the MCBP project:

        enter: 'hamerdirt/codes/MCBP/

   You can get a list of cities, lakes/rivers by using the following search terms:

       enter: 'hammerdirt/city-list/
       enter: 'hammerdirt/water-list/

   The output is an array of objects with the following format:

         object = {'location':x0, 'date':x1, 'length':x2, 'quantity':x3, 'code':x4, 'project':x5}

    Location, code are foreignkey related(if we can use that term here) to the following apis:

         location information (GPS, lake/river, postal code): 'hammerdirt/beaches/'

         code information (material, source, description): 'hammerdirt/codes/'

    Contact roger@hammerdirt.ch for more information.

    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get_object(self, place):
        a = item_data()
        b = HDC_Data.objects.all()
        c, d, e, f = location_list(a), city_list(a), water_list(a), project_list(a)
        g, h, i, j = location_list(b), city_list(b), water_list(b), project_list(b)
        if place in c:
            return location_filter(a, place).values()
        elif place in d:
            return city_filter(a, place).values()
        elif place in  e:
            return water_filter(a,place).values()
        elif place in  f:
            return project_filter(a,place).values()
        elif place in g:
            return location_filter(b, place).values()
        elif place in h:
            return city_filter(b, place).values()
        elif place in  i:
            return water_filter(b, place).values()
        elif place in  j:
            return project_filter(b,place).values()
        else:
            try:
                return AllData.objects.filter(location=place).values()
            except AllData.DoesNotExist:
                raise Http404

    def get(self, request, place, format=None):
        detail = self.get_object(place)
        serializer = AllDataSerial(detail, many=True)
        return Response(serializer.data)
class CreateBeach(generics.CreateAPIView):
    '''
    The is the api for creating survey locations in Europe. This needs to be completed before entering data on a 'new beach'

       1) A login is required
       2) There needs to be an existing project to attribute the beach to

    contact roger@hammerdirt.ch for login information

    '''
    queryset = Beaches.objects.all()
    serializer_class = BeachCreate
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
class CaCreateBeach(generics.CreateAPIView):
    '''
    The is the api for creating survey locations in Europe. This needs to be completed before entering data on a 'new beach'

       1) A login is required
       2) There needs to be an existing project to attribute the beach to

    contact roger@hammerdirt.ch for login information

    '''
    queryset = HDC_Beaches.objects.all()
    serializer_class = HdcBeachCreate
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
@api_view()
def api_home(request):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    return render(request,'dirt/api-home.html')
class BeachApi(APIView):
    """
    This is the searchable api for hammerdirt beach survey locations. Get the geo details for a particular survey site:

        enter: 'hammerdirt/beaches/Vidy' gives you the details for the survey location named 'Vidy'
        enter: 'hammerdirt/beaches/lake' gives you the details for all survey locations on lakes *! This function disbaled for California !
        enter: 'hammerdirt/beaches/Lausanne' gives you the details for all survey locations in the city of Lausanne

    The filter fields are the following:

        'location': get the details for one location

        'city': get the details for all the locations in a city

        *'water':get all the locations for either "lakes"  or "rivers"

        'water_name': get all the locations on a body of water

        'project': get all the locations associated with a project

    The output is an array of objects with the following format:

         object = {'location':x0, 'latitude':x1,'longitude':x2, 'city':x3,'post':x4, 'water':x5,'water_name':x6, 'project':x7}

    Project details are available on the website. Otherwise this API is the most up to date resource for location information. There
    are related endpoints for demographics, discharge rates and lake levels.

    Contact roger@hammerdirt.ch for more information.

    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, name):
        a = Beaches.objects.filter(water='l').values_list('location', flat=True)
        b = Beaches.objects.filter(water='r').values_list('location', flat=True)
        c = Beaches.objects.values_list('location', flat=True)
        d = Beaches.objects.values_list('city', flat=True)
        e = Beaches.objects.values_list('project', flat=True)
        f = Beaches.objects.values_list('water_name', flat=True)
        g = HDC_Beaches.objects.filter(water='l').values_list('location', flat=True)
        h = HDC_Beaches.objects.filter(water='r').values_list('location', flat=True)
        i = HDC_Beaches.objects.values_list('location', flat=True)
        j = HDC_Beaches.objects.values_list('city', flat=True)
        k = HDC_Beaches.objects.values_list('project', flat=True)
        l = HDC_Beaches.objects.values_list('water_name', flat=True)
        if name in c:
            return Beaches.objects.filter(location=name).values()
        elif name in d:
            return Beaches.objects.filter(city=name).values()
        elif name in  f:
            return Beaches.objects.filter(water_name=name).values()
        elif name in  e:
            return Beaches.objects.filter(project=name).values()
        elif name == 'lakes' or name == 'rivers':
            name = name[0]
            return Beaches.objects.filter(water=name).values()
        elif name in i:
            return HDC_Beaches.objects.filter(location=name).values()
        elif name in j:
            return Beaches.objects.filter(city=name).values()
        elif name in  l:
            return Beaches.objects.filter(water_name=name).values()
        elif name in  k:
            return Beaches.objects.filter(project=name).values()
        else:
            try:
                return Beaches.objects.filter(location=name).values()
            except AllData.DoesNotExist:
                raise Http404


    def get(self, request, name, format=None):
        print(name)
        detail = self.get_object(name)
        # print(detail)
        serializer = BeachSerial(detail, many=True)
        return Response(serializer.data)

class CityList(APIView):
    """
    This the list of cities in the hammerdirt beach-litter data base

    contact roger@hammerdirt.ch for more information
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get_object(self):
        a = list(Beaches.objects.values_list('city', flat=True).distinct())
        b = list(HDC_Beaches.objects.values_list('city', flat=True).distinct())
        c = a + b
        return c


    def get(self, request, format=None):
        detail = self.get_object()
        return JsonResponse(detail, safe=False)

class LocationSummary(APIView):
    """
    This is the searchable api for hammerdirt beach litter summaries. Get descriptive statistics for survey locations,
    cities, rivers/lakes or projects.

        enter: 'hammerdirt/summary/Vidy' gives you the summary stats for the survey location named 'Vidy'
        enter: 'hammerdirt/summary/Total' gives you the summary stats for all the survey locations in the database

    The filter fields are the following:

        'location': get the summary details for one location

        'city': get the aggregated summary for all the locations in a city

        'name of lake or river': get the aggregated summary for all the locations on a body of water

        'project': get the aggregated summary for all the locations associated with a project

        'river' or 'lake': get the aggregated summary for all the locations on rivers or lakes


    The output is an object with the following format:

         object = {'first':first-sample, 'last':last-sample, 'num_samps':num of samples, 'ave_dense':average pcs/m, 'min_dense':min pcs/m,
        'max_dense':max pcs/m, 'two_five':25th percentile, 'seven_five':75th percentile, 'stan_dev':standard deviation, 'total':total # of pieces,
         'iqr':inner qaurtile range}

    contact roger@hammerdirt.ch for more information
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get_object(self, water):
        a = item_data()
        b = HDC_Data.objects.all()
        c, d, e, f = location_list(a), city_list(a), water_list(a), project_list(a)
        g, h, i, j = location_list(b), city_list(b), water_list(b), project_list(b)

        if water in c:
            return location_filter(a, water)
        elif water in d:
            return city_filter(a, water)
        elif water in  e:
            return water_filter(a,water)
        elif water in  f:
            return project_filter(a,water)
        elif water in g:
            return location_filter(b, water)
        elif water in h:
            return city_filter(b, water)
        elif water in  i:
            return water_filter(b,water)
        elif water in  j:
            return project_filter(b,water)
        else:
            try:
                return AllData.objects.filter(location=water).values()
            except AllData.DoesNotExist:
                raise Http404


    def get(self, request, water, format=None):
        d = item_summary(self.get_object(water), water)[1]
        detail = {'num_locs':d[0], 'total':d[1], 'num_samps':d[2],'first':d[3], 'last':d[4], 'ave_dense':d[5], 'max_dense':d[6], 'min_dense':d[7], 'two_five':d[8] ,'seven_five':d[9], 'num_lakes':d[10], 'num_rivers':d[11], 'stan_dev':d[12], 'location':d[13]}
        print(detail)
        serializer = SummarySerializer(detail)
        print(serializer.data)
        return Response(serializer.data)



class DailyTotals(APIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get_object(self, location):
        a = item_data()
        b = HDC_Data.objects.all()
        c, d, e, f = location_list(a), city_list(a), water_list(a), project_list(a)
        g, h, i, j = location_list(b), city_list(b), water_list(b), project_list(b)
        if location in c:
            return location_filter(a, location)
        elif location in d:
            return city_filter(a, location)
        elif location in  e:
            return water_filter(a,location)
        elif location in  f:
            return project_filter(a,location)
        elif location in g:
            return location_filter(b, location)
        elif location in h:
            return city_filter(b, location)
        elif location in  i:
            return water_filter(b,location)
        elif location in  j:
            return project_filter(b,location)
        else:
            try:
                return AllData.objects.filter(location=location)
            except AllData.DoesNotExist:
                raise Http404


    def get(self, request, location, format=None):

        detail = self.get_object(location).values('date').annotate(total=Sum('quantity')).values('location', 'date', 'length', 'total')

        serializer = DailyTotalSerial(detail, many=True)
        return Response(serializer.data)
class LitterApiCode(APIView):
    """
    This is the searchable api for hammerdirt beachlitter records. Get all the records for a city, lake/river, project or location.
    The search can be further refined to the object level.  For example to get all the surveys where the G95 code was indentified in Vevey:

         enter: 'hammerdirt/Vevey/G95/

    Valid terms are City, Body of water, Project name, Survey location name. To get all the data for the MCBP project:

        enter: 'hamerdirt/MCBP/

   You can get a list of cities, lakes/rivers by using the following search terms:

       enter: 'hammerdirt/city-list/
       enter: 'hammerdirt/water-list/

   The output is an array of objects with the following format:

         object = {'location':x0, 'date':x1, 'length':x2, 'quantity':x3, 'code':x4, 'project':x5}

    Location, code are foreignkey related(if we can use that term here) to the following apis:

         location information (GPS, lake/river, postal code): 'hammerdirt/beaches/'

         code information (material, source, description): 'hammerdirt/codes/'

    Contact roger@hammerdirt.ch for more information.

    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def get_object(self, place, thing):
        a = item_data()
        b = HDC_Data.objects.all()
        c, d, e, f = location_list(a), city_list(a), water_list(a), project_list(a)
        g, h, i, j = location_list(b), city_list(b), water_list(b), project_list(b)
        if place in c:
            return location_filter(a, place).filter(code=thing).values()
        elif place in d:
            return city_filter(a, place).filter(code=thing).values()
        elif place in  e:
            return water_filter(a,place).filter(code=thing).values()
        elif place in  f:
            return project_filter(a,place).filter(code=thing).values()
        elif place in g:
            return location_filter(b, place).filter(code=thing).values()
        elif place in h:
            return city_filter(b, place).filter(code=thing).values()
        elif place in  i:
            return water_filter(b,place).filter(code=thing).values()
        elif place in  j:
            return project_filter(b,place).filter(code=thing).values()
        else:
            try:
                return AllData.objects.filter(location=place).filter(code=thing).values()
            except AllData.DoesNotExist:
                raise Http404
    def get(self, request, place, thing, format=None):
        print(place, thing)
        detail = self.get_object(place, thing)
        #print(detail)
        serializer = AllDataSerial(detail, many=True)
        return Response(serializer.data)
