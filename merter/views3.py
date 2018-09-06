
from django.shortcuts import render
from merter.models import Project, Code, Event, ItemData, Beach
from django.db.models import Sum, Avg
from statistics import mean

def location_filter(l):
    """
    Returns all the data for a location in the ItemData db.
    """
    return ItemData.objects.filter(location=l)
def project_filter(p):
    """
    Returns all the data for a project in the ItemData db.
    """
    return ItemData.objects.filter(location__project=p)
def water_filter(w):
    """
    Returns all the data for a body of water in the ItemData db.
    """
    return ItemData.objects.filter(location__water_name=w)
def city_filter(c):
    """
    Returns all the data for a body of water in the ItemData db.
    """
    return ItemData.objects.filter(location__city=w)


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
def pcs_m_dict(a):
    """
    Takes the results from daily_pcs_m and returns a dict {'location':[array of pcs/m]}
    """
    b = [c[2] for c in a]
    c = a[0][0]
    return {c:b}
def avg_pcs_m(d):
    """
    Returns the average of the array in pcs_m_dict
    """
    return {key + ', avg pcs/m':round(mean(value),4) for key, value in d.items()}
def max_pcs_m(d):
    """
    Returns the max value of pcs_m_dict
    """
    for key, value in d.items():
        a = {key + ', max pcs/m':max(value)}
    return a
def min_pcs_m(d)
    """
    Returns the min value of pcs_m_dict
    """
    for key, value in d.items():
        a = {key + ', min pcs/m':min(value)}
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
def num_samples(q):
    """
    Returns the number of samples for a query set
    Uses len(value) from the key, value of pcs_m_dict
    """
    d = {key + ', number of samples':len(value) for key, value in q.items()}
    return d

   
    


def merTer(request):
    return render(request, 'merter/MerTer.html')
def index(request):
    return render(request, 'dirt/index.html')
