# beaches/dirt/views.py

from django.db import models
from django.db.models import Sum, Avg, Max, Min
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from dirt.models import SLR_Data, SLR_Density, SLR_Beaches, Beaches, Codes, All_Data, References, SUBJECT_CHOICES, SLR_Area, HDC_Data, HDC_Beaches
from django.contrib.auth.models import User
#from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.conf import settings
import json
import os

import pandas as pd
import math
import numpy as np
from scipy.stats import norm
import scipy.stats

import datetime
from datetime import date
from dateutil.rrule import rrule, MONTHLY


class Water_bodies():
    """
    Manualy generated json file.  Dictionary that assigns location_id to name of the water body.
    """
    n = os.path.join( settings.BASE_DIR, 'dirt/static/water_bodies_hdc.json' )
    o = open(n, 'r')
    p = json.load(o)
    f=os.path.join( settings.BASE_DIR, 'dirt/static/water_bodies.json' )
    f = open(f, 'r')
    a = json.load(f)
    b = sorted(list(a.keys()))
    def make_all(c):
        a = {}
        for b in c:
            for key, value in b.items():
                a.update({key:value})
        return a
    all_water = make_all([a, p])
    # print(a)


class Make_cites():
    """
    functions that combine location_ids from different data-tables and
    assign attributes to location_id.

    combine_it: takes two lists of dicts and combines them; returns list of df records
    beaches_mc, slr: takes a df and assigns a value to the 'project' column, returns list of unique location_ids and a df
    cite_dict: takes df and makes a dict with key = 'location_id' and ensures all values are non null
    river_dict, city_dict: creates dict that assigns sets of location_ids to rivers, lakes and cities

    """
    a_1 = list(Beaches.objects.all().values())
    b_1 = list(SLR_Beaches.objects.all().values())
    c_1 = list(HDC_Beaches.objects.all().values())
    def combine_it(c):
        a = []
        for b in c:
            for d in b:
                if d['water'] == 'l':
                    d['water'] = 'lake'
                if d not in a:
                    a.append(d)
        return a
    a_b_all = combine_it([a_1, b_1,])

    def beaches_mc(b):
        a = pd.DataFrame(b)
        a['project'] = 'MCBP'
        b = a.copy()
        c = list(b['city'].unique())
        return c, b
    mc_cities, a = beaches_mc(a_1)

    def beaches_slr(b):
        a = pd.DataFrame(b)
        a['project'] = 'SLR'
        b = a.copy()
        c = list(b['city'].unique())
        return c, b

    slr_cities, b = beaches_slr(b_1)

    def beaches_hdc(b):
        a = pd.DataFrame(b)
        a['project'] = 'HDC'
        b = a.copy()
        c = list(b['city'].unique())
        return c, b
    hdc_cities, a = beaches_hdc(c_1)


    def cite_dict(a_list):
        d = {}
        a = []
        for dic in a_list:
            if dic['city'] not in a:
                a.append(dic['city'])

            c = {dic['location']:{'latitude':dic['latitude'], 'longitude':dic['longitude'], 'city':dic['city'], 'post':dic['post'], 'project':dic['project_id'], 'water':dic['water']}}
            d.update(c)
            a = sorted(a)
        return d, a
    mc_site_info, mc_cities = cite_dict(a_1)
    slr_cite_info, slr_cites = cite_dict(b_1)
    all_site_list, cities =cite_dict(a_b_all)
    key_list = list(all_site_list.keys())
    hdc_sites, hdc_sites_l = cite_dict(c_1)


    def river_dict(w_d, key_w, a):
        b = {}
        for x in key_w:
            c = w_d[x]
            d = set(c).intersection(a)
            e = {x:d}
            if len(d) > 0:
                b.update(e)
        return b
    slr_rivers = river_dict(Water_bodies.a, list(Water_bodies.a.keys()), list(slr_cite_info.keys()))
    mc_rivers =  river_dict(Water_bodies.a, list(Water_bodies.a.keys()), list(mc_site_info.keys()))
    hdc_rivers = river_dict(Water_bodies.p, list(Water_bodies.p.keys()), list(hdc_sites.keys()))

    def city_dict(l_st, keys, df):
        g = {}
        for x in l_st:
            h = []
            for key in keys:
                if df[key]['city'] == x :
                    h.append(key)
            f = {x:h}

            g.update(f)
        return g
    all_cities = city_dict(cities, key_list, all_site_list)
    all_slr_cities = city_dict(slr_cites, list(slr_cite_info.keys()), slr_cite_info )
    all_mc_cities = city_dict(mc_cities, list(mc_site_info.keys()), mc_site_info )
    all_hdc_cities = city_dict(hdc_cities, list(hdc_sites.keys()), hdc_sites)
    print(all_slr_cities['Lausanne'])
class Make_data():
    """
    Creates dfs from mysql query. loads all tables that hold daily data.
    Formats columns, cuts off all entries greater than today.
    Returns df for all datatables and one aggregated df of all data(slr and mcbp)

    """
    a = pd.DataFrame(list(All_Data.objects.all().values()))
    b = pd.DataFrame(list(SLR_Data.objects.all().values()))
    e = pd.DataFrame(list(SLR_Density.objects.all().values()))
    f = pd.DataFrame(list(SLR_Density.objects.filter(location__water = 'river').values()))
    g = pd.DataFrame(list(SLR_Density.objects.filter(location__water = 'lake').values()))
    i = pd.DataFrame(list(SLR_Area.objects.all().values()))
    k = pd.DataFrame(list(SLR_Area.objects.filter(location__water = 'river').values()))
    l = pd.DataFrame(list(SLR_Area.objects.filter(location__water = 'lake').values()))
    o = pd.DataFrame(list(HDC_Data.objects.all().values()))

    def format_data(y):
        t_day = pd.to_datetime('today')
        a = y.columns
        if 'quantity' in a:
            y = y.astype({'quantity':float}, copy=False)
        if 'density' in a:
            y = y.astype({'density':float}, copy=False)
        if 'density2' in a:
            y = y.astype({'density2':float}, copy=False)
        if 'date' in a:
            y['date'] = pd.to_datetime(y['date'])
            y = y[y.date <= t_day]
        if 'sample' in a:
            y = y.astype({'sample':float}, copy=False)
        if 'length' in a:
            y = y.astype({'length':float}, copy=False)
        # if 'project' not in a:
        #     print('no project')
        return y
    c = format_data(a)
    d = format_data(b)
    h = format_data(e)
    j = format_data(i)
    m = format_data(k)
    n = format_data(l)
    p = format_data(o)
    # print(p)
    river = format_data(f)
    lake = format_data(g)
    all_data = pd.concat([c,d])

class Make_daily():
    """
    daily: takes a df of daily code values, groups quantity by date and location and gets the daily sum of density per location
    and assigns a sample number. returns a df
    daily density: takes a df of daily density values, formats the date to str, creates a list of dicts per daily record,
    gets the log of all densities. returns a dict of records, a list of logs, and two dfs
    daily density 2: same as daily density but for data sets using area and not pcs/m
    all-samples: aggregates list of dicts (record form) in two a single list of dicts. returns a list of dicts and a df
    some of these get passed to directly to a JS function.
    """
    def daily(a, b):
        e =  a['quantity'].groupby([a['date'], a['location_id'], a['length']]).sum().copy()
        e = pd.DataFrame(e)
        e.reset_index(inplace=True)
        e = e[e.date > min(e.date)]
        e['density'] = e['quantity']/e['length']
        e['density'] = e['density'].round(4)
        for name in b:
            n=0
            for i, row in e.iterrows():
                if e.loc[i, 'location_id'] == name:
                    n=n+1
                    e.loc[i, 'sample'] = n
        return e
    c = daily(Make_data.c, Beaches.beachList())
    f = daily(Make_data.p, HDC_Beaches.beachList())
    print(HDC_Beaches.beachList())
    # print(f)
    def daily_density(df):
        a = df[['date', 'location_id', 'density','quantity', 'sample']].copy()
        bb = a[['date', 'location_id', 'density']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return [x, e, bb, a]

    d, d1, d2, d3 = daily_density(Make_data.h)
    e, e1, e2, e3 = daily_density(c)
    r, r1, r2, r3 = daily_density(Make_data.river)
    l, l1, l2, l3 = daily_density(Make_data.lake)
    hd, hd1, hd2, hd3, = daily_density(f)

    def daily_density2(df):
        a = df[['date', 'location_id', 'density2','quantity', 'sample']].copy()
        bb = a[['date', 'location_id', 'density2']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density2'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return [x, e, bb, a]

    ar, ar1, ar2, ar3 = daily_density2(Make_data.j)
    arl, arl1, arl2, arl3 = daily_density2(Make_data.n)
    arr, arr1, arr2, arr3 = daily_density2(Make_data.m)
    def all_samples(e):
        a = []
        c = e
        for v in c:
            for s in v:
                a.append(s)
        b = pd.DataFrame(a)
        return b, a
    all_daily_df, all_daily_list = all_samples([e,d,hd])
    slr_area_daily, slr_area_list = all_samples([ar])

class Make_codes():
    """
    output is dict, list and df.
    attaches material and description to top ten codes
    sorted descending, output is for templates
    """
    codes = Codes.objects.all().values()

    def desc_dict():
        """
        rerturns a dict with key = code_id, value = code description
        """
        b = {}
        for code in Codes.objects.all().values():
            b.update({code['code']:code['description']})
        return b
    codes_dict = desc_dict()
    # print(codes_dict['G27'])

    def material_dict():
        """
        rerturns a dict with key = code_id, value = code material
        """
        b = {}
        for code in Codes.objects.all().values():
            b.update({code['code']:code['material']})
        return b
    codes_material = material_dict()
    # print(codes_material['G27'])

    def top_ten_codes(df, dci, mat):
        """
        rerturns a list of dicts, output is for templates, sorted descending
        returns a df of all values sorted descending by quantity
        """

        a = df['quantity'].groupby(df['code_id']).sum()
        b = a.sort_values(ascending=False)
        d = list(b.index)
        f = []
        for g in d:
            f.append({'code':g, 'description':dci[g], 'material':mat[g], 'total':b[g]})
        return f, b

    all_inventory, inv_df = top_ten_codes(Make_data.all_data, codes_dict, codes_material)
    slr_inventory, inv_series = top_ten_codes(Make_data.d, codes_dict, codes_material)
    mc_inventory, mc_inv_series = top_ten_codes(Make_data.c, codes_dict, codes_material)
    hdc_inventory, hdc_inv_series = top_ten_codes(Make_data.p, codes_dict, codes_material)
class Make_percents():
    def __init__(self, df, dic):
        self.df = df
        self.dic = dic
    def get_percents(self):
        e = {}
        h = {}
        a = self.df.index
        for b in a:
            c = self.dic[b]
            if c not in e.keys():
                e.update({c:[self.df[b]]})
            else:
                e[c].append(self.df[b])
        for key, value in e.items():
            f = sum(value)
            g = {key:f}
            h.update(g)
        return h
class Make_water():

    def get_basin(x):
        """
        gets all daily data, and the water bodies dictionary
        slices the dataframe based on the value of b[x] (where x is a river or lake name)
        a list of location_ids, returns the sliced df
        """
        a = Make_daily.all_daily_df
        b = Water_bodies.a
        c = a.loc[a.location_id.isin(b[x])]
        return c
    def water_dict(x):
        """
        reverses the key value pairs
        answers the question which river is x on?
        """
        f = {}
        a = x
        for b, c in a.items():
            for d in c:
                e = {d:b}
                f.update(e)
        return f
    site_body = water_dict(Water_bodies.a)
    site_body_hdc = water_dict(Water_bodies.p)
class Make_coordinates():
    """
    Generates the out put for a map plot on google maps API
    Includes summary information per location
    Can be passed directly to JS parser
    """
    def map_coords(plot, names, proj, water ):
        a_map = []
        a = plot['density'].groupby(plot['location_id']).mean().round(6)
        b = names
        f = list(a.index)
        for c in f:
            g = names[c]
            e = [float(g['latitude']), float(g['longitude']), float(a[c]), g['post'], g['city'], plot[plot.location_id == c]['date'].count(), c, proj, water]
            a_map.append(e)
        return a_map
    def map_coords2(plot, names, proj, water ):
        a_map = []
        a = plot['density2'].groupby(plot['location_id']).mean().round(6)
        b = names
        f = list(a.index)
        for c in f:
            g = names[c]
            e = [float(g['latitude']), float(g['longitude']), float(a[c]), g['post'], g['city'], plot[plot.location_id == c]['date'].count(), c, proj, water]
            a_map.append(e)
        return a_map

    def coord_list(b):
        """
        Combines the output from map_coords fucntions
        Accepts a list of lists and compbines them
        Output is a list of lists with map information
        """
        a = []
        for v in b:
                for s in v:
                    a.append(s)
        return(a)
    combined_map = coord_list([map_coords(Make_daily.l3,  Make_cites.all_site_list, 'SLR', 'lake'),
    map_coords(Make_daily.r3, Make_cites.all_site_list, 'SLR', 'river'),
    map_coords(Make_daily.e3, Make_cites.all_site_list, 'MCBP', 'lake')])
    mc_map = coord_list([map_coords(Make_daily.e3, Make_cites.all_site_list, 'MCBP', 'lake')])
    hdc_map = coord_list([map_coords(Make_daily.hd3, Make_cites.hdc_sites, 'HDC', 'river' )])

    slr_map = coord_list([map_coords2(Make_daily.arl3,  Make_cites.all_site_list, 'SLR', 'lake'),
    map_coords2(Make_daily.arr3, Make_cites.all_site_list, 'SLR', 'river')])
class Make_totals():
    def get_total():
        """
        aggregates the totals from the various Projects
        returns the grand total and the subtotals
        """
        slr_total = SLR_Data.objects.all().aggregate(t_total = Sum('quantity'))
        mcbp_total = All_Data.objects.all().aggregate(t_total = Sum('quantity'))
        mc_tot = float(mcbp_total['t_total'])
        sl_tot = float(slr_total['t_total'])
        a = mc_tot + sl_tot
        return a, mc_tot, sl_tot
    a, mc_total, sl_total = get_total()

    def get_lakes():
        """
        gets the location_ids assigned to lake from the Make_daily Class
        combines the lists into one, returns the new list and len(list)
        and the total number of operations
        """
        b = list(Make_daily.l2['location_id'].unique())
        e = len(b)
        c = list(Make_daily.e2['location_id'].unique())
        d = len(c)
        h = len(Make_daily.l)
        for f in c:
            b.append(f)
        g = len(b)
        h = len(Make_daily.l) + len(Make_daily.e)

        return b, g, h
    locs_lakes, lake_locs, lake_locs_t = get_lakes()

    def get_rivers():
        """
        gets the location_ids assigned to river from the Make_daily Class
        combines the lists into one, returns the new list and len(list)
        and the total number of operations
        """
        b = list(Make_daily.r2['location_id'].unique())
        e = len(b)
        f = len(Make_daily.r)
        return b, e, f
    riv_locs, riv_num, len_rivs = get_rivers()

    def total_lakes(c):
        """
        assigns body names to categories lake or river
        skips one record for the moment
        returns a dictionary {'lake': [ list of lake names], 'river' ...}
        returns the length of both values
        """
        a = Make_water.site_body
        b = Make_cites.all_site_list

        f={'lake':[], 'river':[]}
        for d in c:
            if d != 'untersee_steckborn_siedlerm':
                if b[d]['water'] == 'lake':
                    if a[d] not in f['lake']:
                        e = a[d]
                        f['lake'].append(e)
                elif b[d]['water'] == 'river':
                    if a[d] not in f['river']:
                        e = a[d]
                        f['river'].append(e)
        g = len(f['lake'])
        h = len(f['river'])
        return f, g, h

    lake_river, no_of_lake, no_of_river = total_lakes(Make_cites.key_list)
    mc_lake_river, mc_no_of_lake, mc_no_of_river = total_lakes(list(Make_cites.mc_site_info.keys()))
    def total_lakes2(c):
        """
        assigns body names to categories lake or river
        skips one record for the moment
        returns a dictionary {'lake': [ list of lake names], 'river' ...}
        returns the length of both values
        """
        a = Make_water.site_body_hdc
        b = Make_cites.hdc_sites

        f={'lake':[], 'river':[]}
        for d in c:
            if d != 'untersee_steckborn_siedlerm':
                if b[d]['water'] == 'lake':
                    if a[d] not in f['lake']:
                        e = a[d]
                        f['lake'].append(e)
                elif b[d]['water'] == 'river':
                    if a[d] not in f['river']:
                        e = a[d]
                        f['river'].append(e)
        g = len(f['lake'])
        h = len(f['river'])
        return f, g, h
    hdc_lake_river, hdc_no_of_lake, hdc_no_of_river = total_lakes2(list(Make_cites.hdc_sites.keys()))

    def make_summary(x):
        # running a df through pd.describe and assigning varaible names to
        # results, putting those in a dict to be passed on
        x['date'] = pd.to_datetime(x['date'])
        f = x.describe()['density']
        num_samps = f['count']
        stan_dev = f['std'].round(2)
        dens_min = f['min'].round(4)
        dens_max = f['max'].round(2)
        two_five = f['25%'].round(2)
        seven_five = f['75%'].round(2)
        average = f['mean'].round(2)
        first_sample = min(x['date'])
        last_sample = max(x['date'])
        total = x['quantity'].sum()
        iqr = seven_five - two_five
        locs = x['location_id'].unique()
        num_location = len(locs)
        q = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
        'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
        return q, num_location
    all_summary, number_location = make_summary(Make_daily.all_daily_df)
    def make_summary2(x):
        # running a df through pd.describe and assigning varaible names to
        # results, putting those in a dict to be passed on
        x['date'] = pd.to_datetime(x['date'])
        f = x.describe()['density2']
        num_samps = f['count']
        stan_dev = f['std'].round(2)
        dens_min = f['min'].round(4)
        dens_max = f['max'].round(2)
        two_five = f['25%'].round(2)
        seven_five = f['75%'].round(2)
        average = f['mean'].round(2)
        first_sample = min(x['date'])
        last_sample = max(x['date'])
        total = x['quantity'].sum()
        iqr = seven_five - two_five
        locs = x['location_id'].unique()
        num_location = len(locs)
        q = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
        'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
        return q, num_location
class make_months():
    first_day = datetime.date(2015,11,15)
    t_day = datetime.date.today()
    dates = [dt.strftime("%b - %Y") for dt in rrule(MONTHLY, dtstart=first_day, until=t_day)]
class Make_boxes():
    def box_plots(a):
        #mon_dict = {1:'jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'July', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        i = []
        c = a['density'].groupby([a.date.dt.year, a.date.dt.month]).describe()
        c.index.rename(['year', 'month',], inplace=True)
        c.reset_index(inplace=True)
        c['year'] = c['year'].astype(int)
        c['month'] = c['month'].astype(int)
        c['m_y'] = list(zip(c.month, c.year))
        want = ['m_y', 'min', '25%', '50%', '75%', 'max']
        f = len(c['m_y'])
        g = list(range(0, f))
        for d in g:
            h = c.loc[d]
            b_date = datetime.date(year=h.m_y[1], month=h.m_y[0], day=27)
            b_date = b_date.strftime("%Y-%m-%d")
            bx_ix = [b_date, h[want[1]], h[want[2]].round(3), h[want[3]].round(3), h[want[4]].round(3), h[want[5]].round(3)]
            i.append(bx_ix)
        #print(i)
        return i


    river_box = box_plots(Make_daily.r2)
    lake_box = box_plots(Make_daily.l2)
    mc_box = box_plots(Make_daily.e2)
    s_box = box_plots(Make_daily.d2)
    def box_plots2(a):
        #mon_dict = {1:'jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'July', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        i = []
        c = a['density2'].groupby([a.date.dt.year, a.date.dt.month]).describe()
        c.index.rename(['year', 'month',], inplace=True)
        c.reset_index(inplace=True)
        c['year'] = c['year'].astype(int)
        c['month'] = c['month'].astype(int)
        c['m_y'] = list(zip(c.month, c.year))
        want = ['m_y', 'min', '25%', '50%', '75%', 'max']
        f = len(c['m_y'])
        g = list(range(0, f))
        for d in g:
            h = c.loc[d]
            b_date = datetime.date(year=h.m_y[1], month=h.m_y[0], day=27)
            b_date = b_date.strftime("%Y-%m-%d")
            bx_ix = [b_date, h[want[1]], h[want[2]].round(3), h[want[3]].round(3), h[want[4]].round(3), h[want[5]].round(3)]
            i.append(bx_ix)
        #print(i)
        return i
    river_box2 = box_plots2(Make_daily.arr2)
    lake_box2 = box_plots2(Make_daily.arl2)
    s_box2 = box_plots2(Make_daily.ar2)

    def box_cats(x):
        if x == 'SLR':
            first_day = datetime.date(2017,4,1)
        elif x == 'MCBP':
            first_day = datetime.date(2015,11,15)
        elif x == null:
            first_day = datetime.date(2015,11,15)

        t_day = datetime.date.today()
        dates = [dt.strftime("%b-%Y") for dt in rrule(MONTHLY, dtstart=first_day, until=t_day)]
        return dates
class Make_logs():
    """
    creates the output to plot normal dists from density data
    """
    def lake_river_prob(name):
        e = Make_daily.all_daily_df.loc[Make_daily.all_daily_df.location_id.isin(Water_bodies.a[name])]
        d = list(e['location_id'].unique())
        num_locs = len(d)

        return  e, num_locs, d

    def by_date(df, start, end):
        a = df.loc[(df.date > start)&(df.date < end)].copy()
        a['date'] = pd.to_datetime(a['date'])
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        return a

    def get_log_of(df):
        a = df.sort_values('density').copy()
        a['ln'] = np.log(a['density'])
        locate = np.mean(a['ln'])
        scale = np.std(a['ln'])
        a['y'] = norm.pdf(a['ln'], locate, scale)
        x = list(a['ln'])
        y = list(a['y'])
        return locate, scale, x, y
class Make_library():
    library = list(References.objects.all().values())

    def subjects():
        sub_list = References.objects.all().values_list('subject', flat=True).distinct()
        sub_key = dict(SUBJECT_CHOICES)
        return sub_list, sub_key
    the_subs, sub_key = subjects()
    # print('break')
    # print(sub_key)


    def make_library(b,d,f ):
        h = {}
        for a in b:
            c = d[a]
            e = {c:[]}
            for t in f:
                if t['subject'] == a:
                    e[c].append(t)
            h.update(e)
        #     print('break')
        # print(h['Math - probability'])
        return h
    books = make_library(the_subs, sub_key, library)


def beach_litter(request):
    t_day = pd.to_datetime('today')

    ### this is for the combined data section ###
    combined_map = Make_coordinates.combined_map
    summary_df = Make_daily.all_daily_df
    inventory = Make_codes.all_inventory
    top_ten = Make_codes.inv_df

    num_lakes = Make_totals.no_of_lake
    num_rivers = Make_totals.no_of_river
    summary, num_location = Make_totals.all_summary, Make_totals.number_location
    bodies_dict = Water_bodies.a
    bodies_list = Water_bodies.b
    box_lake = Make_boxes.lake_box
    box_river = Make_boxes.river_box
    box_mc = Make_boxes.mc_box
    mk_pers = Make_percents(Make_codes.inv_df, Make_codes.codes_material).get_percents()

    def material_as_percent(d):
        a = summary['total']
        h = {}
        for b, c in d.items():
            e = (c/a )*100
            f = [c,e]
            g = {b:f}
            h.update(g)
        return h
    def top_ten_percents(e):
        a = summary['total']
        b = []
        for c in e:
            c.update({'per':(c['total']/a)*100})

            b.append(c)

        return b

    top_list = inventory[:10]

    top_ten_table = top_ten_percents(top_list)

    mk_pers = material_as_percent(mk_pers)

    ### end combined data ###

    #### this is specific to the section the probability of garbage ###

    plot_all = Make_daily.all_daily_list

    # getting the data and separating in two date groups
    summary_df_x, num_locs, loc_list  = Make_logs.lake_river_prob("Lac Léman")
    a = Make_logs.by_date(summary_df_x, "2015-11-15", "2016-11-15")
    b = Make_logs.by_date(summary_df_x, "2016-11-15", "2017-11-15")

    # get the components to sketch the distributions
    loc, scale, x_one, y_one = Make_logs.get_log_of(a)
    loc2, scale2, x_two, y_two = Make_logs.get_log_of(b)

    # put this in a format for js
    def make_dists(a, b):
        f =[]
        for c, d in enumerate(a):
            e = [a[c], b[c]]
            f.append(e)
        return f

    # these are for the distro plots
    dist_2016 = make_dists(x_one, y_one)
    dist_2017 = make_dists(x_two, y_two)

    # these are for the by date scatter
    plot_density =  a.to_dict(orient='records')
    plot_mc =  b.to_dict(orient='records')

    num_samps = len(summary_df_x)


    return render(request, 'dirt/beach_litter.html', { 'mk_pers':mk_pers, 'top_ten':top_ten_table, 'top_ten_total': top_ten[:10].sum(),'all_water':Water_bodies.b,
    'all_cities':Make_cites.cities, 'plot_all':plot_all, 'y_one_s':len(plot_density), 'y_two_s':len(plot_mc), 'year_one':plot_density, 'year_two':plot_mc, 'combined_map':combined_map,
    'num_locs':num_location, 'dist_2016':dist_2016,'dist_2017':dist_2017 , 'num_samps':num_samps, 't_day':t_day, 'inventory':inventory, 'bodies_dict':bodies_dict, 'bodies_list':bodies_list,
    'num_lakes':num_lakes, 'num_rivers':num_rivers,'summary':summary,'box_lake':box_lake, 'box_river':box_river, 'box_mc':box_mc, 'lakes':Make_daily.l, 'rivers':Make_daily.r,'plot_mc':Make_daily.e})

def services_home(request):
    return render(request, 'dirt/services.html')
def in_the_works(request):
    return render(request, 'dirt/intheworks.html')
def microbiology(request):
    # url = staticfiles_storage.url('data/foobar.csv')
    # my_jsons = '/statihome/mw-shovel/web/notes/micro/data/json/'
    def get_jsons_x(file_name):
        with open(os.path.join( settings.BASE_DIR, 'dirt/static/jsons/' + file_name ), 'r') as f:
            a = json.load(f)
            return a
    #f=os.path.join( settings.BASE_DIR, 'dirt/static/jsons/' + file_name )
    mrd_map = get_jsons_x('summ_mrd_map.json')
    t_cfu_17 = get_jsons_x('t_cfu_17.json')
    t_uv_17 = get_jsons_x('total_uv17.json')
    rain_17 = get_jsons_x('rain_17.json')
    rain_16 = get_jsons_x('rain_16.json')
    big_blue17 = get_jsons_x('big_blue17.json')
    big_blue16 = get_jsons_x('big_blue16.json')
    t_cfu_16 = get_jsons_x('t_cfu_16.json')
    books = Make_library.books
    return render(request, 'dirt/microbiology.html', {'b_blue17_svt':big_blue17[2], 'b_blue17_vnx':big_blue17[1], 'b_blue17_mrd':big_blue17[0],
                'rain_17':rain_17, 'map_points':mrd_map, 'books':books, 't_cfu_17_mrd':t_cfu_17[0], 't_cfu_17_vnx': t_cfu_17[1],
                't_cfu_17_svt': t_cfu_17[2], 't_uv_17_svt':t_uv_17[2], 't_uv_17_mrd':t_uv_17[0], 't_uv_17_vnx':t_uv_17[1],
                'b_blue16_svt':big_blue16[2], 'b_blue16_vnx':big_blue16[1], 'b_blue16_mrd':big_blue16[0], 't_cfu_16_mrd':t_cfu_16[0], 't_cfu_16_vnx': t_cfu_16[1],
                't_cfu_16_svt': t_cfu_16[2], 'rain_16':rain_16})
def index(request):
    return render(request, 'dirt/index.html')

def search_city(request):
    if 'city' in request.GET and request.GET['city']:
        q = request.GET['city']
        print(q)

        t_day = pd.to_datetime('today')
        # dcitionary that relates location id to waterbody
        water_bodies = Make_cites.all_cities

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = Make_daily.all_daily_df
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Make_daily.daily_density(a)

            return c_1, c_2, c_3, c_4
        # c_1 = a list of dicts in form df-record per dict
        # c_2 = a list of np.log() values for daily pcs/m
        # c_3 = a df with 'date', 'location_id', 'density'
        # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data = Make_data.all_data.loc[Make_data.all_data.location_id.isin(water_bodies[q])].copy()

        # data for table 'locations, samples and avgerages'
        # groups c_4 by location id, aggregates density and sample no
        # ourputs data to dict for js output

        def locs_and_samples():
            a = c_4.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        # Materioal and Topten functions:
        # use the code id attributes to sort and aggregate results
        # creates a dict of top_ten and material, ourput is for js
        def material_as_percent(d):
            a = summary['total']
            h = {}
            for b, c in d.items():
                e = (c/a )*100
                f = [c,e]
                g = {b:f}
                h.update(g)
            return h
        def top_ten_percents(e):
            a = summary['total']
            b = []
            for c in e:
                c.update({'per':(c['total']/a)*100})
                b.append(c)
            return b

        total_inventory, city_top_ten = Make_codes.top_ten_codes(code_data, Make_codes.codes_dict, Make_codes.codes_material)
        t_ten = top_ten_percents(total_inventory[:10])
        mk_pers = Make_percents(city_top_ten, Make_codes.codes_material).get_percents()
        mk_pers = material_as_percent(mk_pers)

        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        return render(request, 'dirt/search_city.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': Make_daily.all_daily_list,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.b, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')

def search_water(request):
    if 'water' in request.GET and request.GET['water']:
        q = request.GET['water']
        print(q)

        t_day = pd.to_datetime('today')
        # dcitionary that relates location id to waterbody
        water_bodies = Water_bodies.a

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = Make_daily.all_daily_df
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Make_daily.daily_density(a)

            return c_1, c_2, c_3, c_4

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data = Make_data.all_data.loc[Make_data.all_data.location_id.isin(water_bodies[q])].copy()

        # data for table 'locations, maples and avgerages
        # use the df pulled and sorted strting with 'a'
        # draws a default pd.describe and stores in a dictionary
        # output for js
        def locs_and_samples():
            a = c_4.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        # Materioal and Topen functions:
        # use the code id sttributes to sort and aggregate results
        # gets percent baluse by id and material, sorts descending
        def material_as_percent(d):
            a = summary['total']
            h = {}
            for b, c in d.items():
                e = (c/a )*100
                f = [c,e]
                g = {b:f}
                h.update(g)
            return h
        def top_ten_percents(e):
            a = summary['total']
            b = []
            for c in e:
                c.update({'per':(c['total']/a)*100})
                b.append(c)
            return b

        total_inventory, city_top_ten = Make_codes.top_ten_codes(code_data, Make_codes.codes_dict, Make_codes.codes_material)
        t_ten = top_ten_percents(total_inventory[:10])
        mk_pers = Make_percents(city_top_ten, Make_codes.codes_material).get_percents()
        mk_pers = material_as_percent(mk_pers)

        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        return render(request, 'dirt/search_water.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': Make_daily.all_daily_list,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.b, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')

def search_SLR(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        print(q)

        t_day = pd.to_datetime('today')
        # dcitionary that relates location id to waterbody
        water_bodies = Make_cites.all_cities

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = Make_daily.slr_area_daily
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Make_daily.daily_density2(a)

            return c_1, c_2, c_3, c_4
        # c_1 = a list of dicts in form df-record per dict
        # c_2 = a list of np.log() values for daily pcs/m
        # c_3 = a df with 'date', 'location_id', 'density'
        # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary2(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords2(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data = Make_data.all_data.loc[Make_data.all_data.location_id.isin(water_bodies[q])].copy()

        # data for table 'locations, samples and avgerages'
        # groups c_4 by location id, aggregates density and sample no
        # ourputs data to dict for js output

        def locs_and_samples():
            a = c_4.groupby('location_id')
            b = a.agg({'density2':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        # Materioal and Topten functions:
        # use the code id attributes to sort and aggregate results
        # creates a dict of top_ten and material, ourput is for js
        def material_as_percent(d):
            a = summary['total']
            h = {}
            for b, c in d.items():
                e = (c/a )*100
                f = [c,e]
                g = {b:f}
                h.update(g)
            return h
        def top_ten_percents(e):
            a = summary['total']
            b = []
            for c in e:
                c.update({'per':(c['total']/a)*100})
                b.append(c)
            return b

        total_inventory, city_top_ten = Make_codes.top_ten_codes(code_data, Make_codes.codes_dict, Make_codes.codes_material)
        t_ten = top_ten_percents(total_inventory[:10])
        mk_pers = Make_percents(city_top_ten, Make_codes.codes_material).get_percents()
        mk_pers = material_as_percent(mk_pers)

        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        return render(request, 'dirt/search_slr.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': Make_daily.ar,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density2']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.b, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')



def search_MCBP(request):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']
            print('break!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(q)

            t_day = pd.to_datetime('today')
            # dcitionary that relates location id to waterbody
            water_bodies = Make_cites.all_mc_cities

            # this gets the data for the report
            def get_daily_values(criteria):
                # gets the values associated with the user choice
                # sets the date and time stamp
                # calls Make_daily to sort and make different lists\
                a = Make_daily.e3
                a['date'] = pd.to_datetime(a['date'])
                a = a.loc[a.location_id.isin(water_bodies[criteria])]
                c_1, c_2, c_3, c_4 = Make_daily.daily_density(a)

                return c_1, c_2, c_3, c_4
            # c_1 = a list of dicts in form df-record per dict
            # c_2 = a list of np.log() values for daily pcs/m
            # c_3 = a df with 'date', 'location_id', 'density'
            # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

            c_1, c_2, c_3, c_4 = get_daily_values(q)


            summary, num_locs= Make_totals.make_summary(c_4)

            map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.mc_site_info, 'MCBP', q)])
            code_data = Make_data.c.loc[Make_data.c.location_id.isin(water_bodies[q])].copy()

            # data for table 'locations, samples and avgerages'
            # groups c_4 by location id, aggregates density and sample no
            # ourputs data to dict for js output

            def locs_and_samples():
                a = c_4.groupby('location_id')
                b = a.agg({'density':np.mean, 'sample':max})
                b.reset_index(inplace=True)
                c = b.to_dict('records')
                return c

            # Materioal and Topten functions:
            # use the code id attributes to sort and aggregate results
            # creates a dict of top_ten and material, ourput is for js
            def material_as_percent(d):
                a = summary['total']
                h = {}
                for b, c in d.items():
                    e = (c/a )*100
                    f = [c,e]
                    g = {b:f}
                    h.update(g)
                return h
            def top_ten_percents(e):
                a = summary['total']
                b = []
                for c in e:
                    c.update({'per':(c['total']/a)*100})
                    b.append(c)
                return b

            total_inventory, city_top_ten = Make_codes.top_ten_codes(code_data, Make_codes.codes_dict, Make_codes.codes_material)
            t_ten = top_ten_percents(total_inventory[:10])
            mk_pers = Make_percents(city_top_ten, Make_codes.codes_material).get_percents()
            mk_pers = material_as_percent(mk_pers)

            color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

            return render(request, 'dirt/search_MCBP.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
            'plot_density':c_1,'plot_all': Make_daily.e,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
            'all_water':Water_bodies.b, 'all_cities':Make_cites.cities,})

        else:
            return HttpResponse('Please submit a search term')



def slr_home(request):

    slr_locs = SLR_Beaches.beachList()
    slr_beaches = SLR_Beaches.objects.all().values()


    summary, number_locations = Make_totals.make_summary2(Make_data.j)
    map_points = Make_coordinates.slr_map
    inventory = Make_codes.slr_inventory
    mk_pers = Make_percents(Make_codes.inv_series, Make_codes.codes_material).get_percents()

    books = Make_library.books

    def city_list(city_query):
        b = []
        a = list(city_query['location_id'].unique())
        for c in a :
            d = Make_cites.slr_cite_info[c]['city']
            if d not in b:
                b.append(d)

        b=sorted(b)
        return b
    cities = city_list(Make_daily.ar3)

    def top_ten_percents(e):
        a = summary['total']
        b = []
        for c in e:
            c.update({'per':(c['total']/a)*100})
            b.append(c)
        return b

    top_ten_table = top_ten_percents(inventory[:10])

    def material_as_percent(d):
        a = summary['total']
        h = {}
        for b, c in d.items():
            e = (c/a )*100
            f = [c,e]
            g = {b:f}
            h.update(g)
        return h
    mk_pers = material_as_percent(mk_pers)

    color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

    def locs_and_samples():
        a =  Make_data.j.groupby('location_id')
        b = a.agg({'density2':np.mean, 'sample':max})
        b.reset_index(inplace=True)
        c = b.to_dict('records')
        return c

    return render(request, 'dirt/slr.html', {'books':books, 'num_lakes':Make_totals.no_of_lake, 'num_rivers':Make_totals.no_of_river,
    'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Make_daily.ar,
    'map_points':map_points, 'slr_cities': cities,'box_plot': Make_boxes.s_box2, 'box_cats':Make_boxes.box_cats('SLR'),
    'lakes':Make_daily.arl, 'rivers':Make_daily.arr, 'box_lake':Make_boxes.lake_box2, 'box_river':Make_boxes.river_box2,
    'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_slr_cities, 'slr_river':Make_cites.slr_rivers,
    'all_water':Water_bodies.b, 'all_cities':Make_cites.cities})

def mcbp_home(request):
        slr_locs = Beaches.beachList()
        slr_beaches = Beaches.objects.all().values()
        # codes = Codes.objects.all()

        summary, number_locations = Make_totals.make_summary(Make_daily.c)
        map_points = Make_coordinates.mc_map
        inventory = Make_codes.mc_inventory
        mk_pers = Make_percents(Make_codes.mc_inv_series, Make_codes.codes_material).get_percents()

        books = Make_library.books

        def city_list(city_query):
            b = []
            a = list(city_query)
            for x in a:
                if x['city'] not in b:
                    b.append(x['city'])
            b=sorted(b)
            return b
        cities = city_list(slr_beaches)

        def top_ten_percents(e):
            a = summary['total']
            b = []
            for c in e:
                c.update({'per':(c['total']/a)*100})
                b.append(c)
            return b

        top_ten_table = top_ten_percents(inventory[:10])

        def material_as_percent(d):
            a = summary['total']
            h = {}
            for b, c in d.items():
                e = (c/a )*100
                f = [c,e]
                g = {b:f}
                h.update(g)
            return h
        mk_pers = material_as_percent(mk_pers)

        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        def locs_and_samples():
            a =  Make_daily.c.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        return render(request, 'dirt/mcbp.html', {'books':books, 'num_lakes':Make_totals.mc_no_of_lake, 'num_rivers':Make_totals.mc_no_of_river,
        'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Make_daily.e,
        'map_points':map_points, 'slr_cities': cities,'box_plot':Make_boxes.mc_box, 'box_cats':Make_boxes.box_cats('SLR'),
        'lakes':Make_daily.l, 'rivers':Make_daily.r, 'box_lake':Make_boxes.lake_box, 'box_river':Make_boxes.river_box,
        'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_mc_cities, 'slr_river':Make_cites.mc_rivers,
        'all_water':Water_bodies.b, 'all_cities':Make_cites.cities})

def hdc_home(request):
        slr_locs = HDC_Beaches.beachList()
        slr_beaches = HDC_Beaches.objects.all().values()
        # codes = Codes.objects.all()

        summary, number_locations = Make_totals.make_summary(Make_daily.f)
        map_points = Make_coordinates.hdc_map
        print(map_points)
        inventory = Make_codes.hdc_inventory
        mk_pers = Make_percents(Make_codes.hdc_inv_series, Make_codes.codes_material).get_percents()

        books = Make_library.books

        def city_list(city_query):
            b = []
            a = list(city_query)
            for x in a:
                if x['city'] not in b:
                    b.append(x['city'])
            b=sorted(b)
            return b
        cities = city_list(slr_beaches)

        def top_ten_percents(e):
            a = summary['total']
            b = []
            for c in e:
                c.update({'per':(c['total']/a)*100})
                b.append(c)
            return b

        top_ten_table = top_ten_percents(inventory[:10])

        def material_as_percent(d):
            a = summary['total']
            h = {}
            for b, c in d.items():
                e = (c/a )*100
                f = [c,e]
                g = {b:f}
                h.update(g)
            return h
        mk_pers = material_as_percent(mk_pers)

        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        def locs_and_samples():
            a =  Make_daily.f.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        return render(request, 'dirt/hdc.html', {'books':books, 'num_lakes':Make_totals.hdc_no_of_lake, 'num_rivers':Make_totals.hdc_no_of_river,
        'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Make_daily.hd,
        'map_points':map_points, 'slr_cities': cities,'box_plot':Make_boxes.mc_box, 'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_hdc_cities, 'slr_river':Make_cites.hdc_rivers,
        'all_water':Water_bodies.a, 'all_cities':Make_cites.cities})

def search_hdc(request):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']
            print('break!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(q)

            t_day = pd.to_datetime('today')
            # dcitionary that relates location id to waterbody
            water_bodies = Make_cites.all_hdc_cities

            # this gets the data for the report
            def get_daily_values(criteria):
                # gets the values associated with the user choice
                # sets the date and time stamp
                # calls Make_daily to sort and make different lists\
                a = Make_daily.hd3
                a['date'] = pd.to_datetime(a['date'])
                a = a.loc[a.location_id.isin(water_bodies[criteria])]
                c_1, c_2, c_3, c_4 = Make_daily.daily_density(a)

                return c_1, c_2, c_3, c_4
            # c_1 = a list of dicts in form df-record per dict
            # c_2 = a list of np.log() values for daily pcs/m
            # c_3 = a df with 'date', 'location_id', 'density'
            # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

            c_1, c_2, c_3, c_4 = get_daily_values(q)


            summary, num_locs= Make_totals.make_summary(c_4)

            map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.hdc_sites, 'HDC', q)])
            code_data = Make_data.p.loc[Make_data.p.location_id.isin(water_bodies[q])].copy()

            # data for table 'locations, samples and avgerages'
            # groups c_4 by location id, aggregates density and sample no
            # ourputs data to dict for js output

            def locs_and_samples():
                a = c_4.groupby('location_id')
                b = a.agg({'density':np.mean, 'sample':max})
                b.reset_index(inplace=True)
                c = b.to_dict('records')
                return c

            # Materioal and Topten functions:
            # use the code id attributes to sort and aggregate results
            # creates a dict of top_ten and material, ourput is for js
            def material_as_percent(d):
                a = summary['total']
                h = {}
                for b, c in d.items():
                    e = (c/a )*100
                    f = [c,e]
                    g = {b:f}
                    h.update(g)
                return h
            def top_ten_percents(e):
                a = summary['total']
                b = []
                for c in e:
                    c.update({'per':(c['total']/a)*100})
                    b.append(c)
                return b

            total_inventory, city_top_ten = Make_codes.top_ten_codes(code_data, Make_codes.codes_dict, Make_codes.codes_material)
            t_ten = top_ten_percents(total_inventory[:10])
            mk_pers = Make_percents(city_top_ten, Make_codes.codes_material).get_percents()
            mk_pers = material_as_percent(mk_pers)

            color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

            return render(request, 'dirt/search_hdc.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
            'plot_density':c_1,'plot_all': Make_daily.hd,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
            'all_water':Water_bodies.b, 'all_cities':Make_cites.cities,})

        else:
            return HttpResponse('Please submit a search term')
