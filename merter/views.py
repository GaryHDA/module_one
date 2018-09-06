
from django.shortcuts import render
from merter.models import Project, Code, Event, ItemData, Beach
from django.db.models import Sum, Avg
from statistics import mean
from dirt.models import AllData
import numpy as np

def item_data():
    """
    Initial query of all item counts
    """
    return AllData.objects.all()
def location_filter(q,l):
    """
    Returns all the data for a location in the ItemData db.
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
    return q.values_list('location__city', flat=True).distinct().order_by()
def project_list(q):
    return q.values_list('location__project', flat=True).distinct().order_by()
def location_list(q):
    return q.values_list('location', flat=True).distinct().order_by()
def water_list(q):
    return q.values_list('location__water_name', flat=True).distinct().order_by()

def location_sub_q(q,l):
    """
    Returns all the data for a location in a project, city or water query.
    Use this to generate the data for tables in the city out put.
    """
    return q.filter(location=l)

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
def daily_pcs_m(t):
    """
    Takes the results of daily_total and divides by length.
    Returns an array of arrays [['location', 'date', 'pcs/m'].....['location', 'date', 'pcs/m']]
    """
    a = []
    for b in t:
        c = b[3]/b[2]
        c = round(c, 4)
        d = [b[0], b[1], c]
        a.append(d)
    return a
def pcs_m_tup(a,l):
    """
    Takes the results from daily_pcs_m and returns a tuple ('location',[array of pcs/m])
    """
    b = [c[2] for c in a]
    return (l,b)
def avg_pcs_m(t):
    """
    Returns the average of the array in pcs_m_tup
    """
    return (t[0] + ', avg pcs/m', round(mean(t[1]),4))
def max_pcs_m(t):
    """
    Returns the max value of pcs_m_dict
    """
    a = (t[0] + ', max pcs/m',max(t[1]))
    return a
def min_pcs_m(t):
    """
    Returns the min value of pcs_m_dict
    """
    a = (t[0] + ', min pcs/m', min(t[1]))
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
    Uses len(value) from the key, value of pcs_m_dict
    """
    return (t[0] + ', number of samples', len(t[1]))
def twenty_fith(t):
    a = np.array(t[1])
    return np.percentile(a, 25)
def seventy_fifth(t):
    a = np.array(t[1])
    return np.percentile(a, 75)
def number_of_locations_region(q):
    return len(location_list(q))
def beaches_in_a_region(q,c):
    a = []
    for b in c:
        d = location_sub_q(q,b)
        f = daily_total(d)
        c = pcs_m_tup(daily_pcs_m(f))
        e = (b, num_samples(c[1]), avg_pcs_m(c[1]))
        a.append(e)
    return a

def all_pcs_m(q,l):
    a = daily_total(q)
    b = daily_pcs_m(a)
    return pcs_m_tup(b, l), b 
    
def item_summary(q, l):
    a = location_total(q)
    b, n = all_pcs_m(q, l)
    c = max_pcs_m(b)
    d = min_pcs_m(b)
    e = twenty_fith(b)
    f = seventy_fifth(b)
    g = num_samples(b)
    h = number_of_locations_region(q)
    i = first_sample(q)
    j = last_sample(q)
    k = max_pcs_m(b)
    l = min_pcs_m(b)
    m = avg_pcs_m(b)
    return [a, c, d, e, f, g, h, i, j, k, l, m]
   
         
    


def merTer(request):
    return render(request, 'merter/MerTer.html')
def index(request):
    return render(request, 'dirt/index.html')
