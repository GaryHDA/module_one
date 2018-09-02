# beaches/dirt/views.py

from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from dirt.models import SLR_Data, SLR_Density, SLR_Beaches, Beaches, Codes, AllData, References, SUBJECT_CHOICES, SLR_Area, HDC_Data, HDC_Beaches, Precious, Descente
from django.conf import settings

import json
import os
import pandas as pd
import math
import numpy as np
from scipy.stats import norm
import datetime


class Water_bodies():
    """
    Creates dictionary that has river or lake name as key and all the locations that are situated on that water body.
    Pulls the data from the Beaches, SLR_Beaches and HDC_Beaches models

    """
    a = list(Beaches.objects.all().exclude(project='MWP').values())
    b = list(SLR_Beaches.objects.all().values())
    c = list(HDC_Beaches.objects.all().values())
    d = list(Beaches.objects.all().exclude(project='MCBP').values())

    def make_water_bodies(x):
        b = {}
        for c in x:
            for h in c:
                d = h['location']
#                e = h['water']
                f = h['water_name']
                g = list(b.keys())
                if f not in g:
                    b.update({f:[d]})
                elif f in g:
                    b[f].append(d)
        return b

    swiss = make_water_bodies([a,b])
    hdc = make_water_bodies([c])
    p_w = make_water_bodies([d])


class Make_cites():
    """
    functions that combine location_ids from different data-tables and
    assign attributes to location_id.

    combine_it: takes two lists of dicts and combines them; returns list of df records
    beaches_mc, slr: takes a df and assigns a value to the 'project' column, returns list of unique location_ids and a df
    cite_dict: takes df and makes a dict with key = 'location_id' and ensures all values are non null
    river_dict, city_dict: creates dict that assigns sets of location_ids to rivers, lakes and cities

    """
    print()
    a_1 = list(Beaches.objects.filter(project = 'MCBP').values())
    a_2 = list(Beaches.objects.filter(project = 'PC').values())
    a_3 = list(Beaches.objects.filter(project = 'MWP').values())
    b_1 = list(SLR_Beaches.objects.all().values())
    c_1 = list(HDC_Beaches.objects.all().values())
    def combine_it(c):
        a = []
        for b in c:
            for d in b:
                if d not in a:
                    a.append(d)
        return a
    a_b_all = combine_it([a_1, b_1, a_2])
    p_all = combine_it([a_2, a_3])

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
    hdc_sites, hdc_cities = cite_dict(c_1)
    p_sites, p_cities = cite_dict(p_all)


    def river_dict(w_d, key_w, a):
        b = {}
        for x in key_w:
            c = w_d[x]
            d = set(c).intersection(a)
            e = {x:d}
            if len(d) > 0:
                b.update(e)
        return b
    slr_rivers = river_dict(Water_bodies.swiss, list(Water_bodies.swiss.keys()), list(slr_cite_info.keys()))
    mc_rivers =  river_dict(Water_bodies.swiss, list(Water_bodies.swiss.keys()), list(mc_site_info.keys()))
    hdc_rivers = river_dict(Water_bodies.hdc, list(Water_bodies.hdc.keys()), list(hdc_sites.keys()))
    p_rivers = river_dict(Water_bodies.p_w, list(Water_bodies.p_w.keys()), list(p_sites.keys()))

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
    all_p_cities = city_dict(p_cities, list(p_sites), p_sites)

    def make_lakes(b, e):
        d = []
        for x in b:
            if x['water'] == e:
                c = x['location']
                d.append(c)
        return d
    mc_lake = make_lakes(a_1,'l')
    mc_river = make_lakes(a_1, 'r')
    p_lake = make_lakes(a_2, 'l')
    p_river = make_lakes(a_2, 'r')
    d_lake = make_lakes(a_3, 'l')
    d_river = make_lakes(a_3, 'r')
    print(mc_river, mc_lake)
class Make_csvs():
    a = pd.DataFrame(Make_cites.a_b_all)
    a.to_csv('dirt/static/site_data.csv', encoding='latin1')

class Mc_data():
    a = pd.DataFrame(list(AllData.objects.all().values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Hdc_data():
    a =  pd.DataFrame(list(HDC_Data.objects.all().values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class P_data():
    a =  pd.DataFrame(list(Precious.objects.all().values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class D_data():
    a =  pd.DataFrame(list(Descente.objects.all().values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)

class Slr_data():
    a = pd.DataFrame(list(SLR_Data.objects.all().exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density' in y.columns:
            y = y.astype({'density':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_density():
    a = pd.DataFrame(list(SLR_Density.objects.all().exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density' in y.columns:
            y = y.astype({'density':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_river():
    a = pd.DataFrame(list(SLR_Density.objects.filter(location__water = 'r').exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density' in y.columns:
            y = y.astype({'density':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_lake():
    a = pd.DataFrame(list(SLR_Density.objects.filter(location__water = 'l').exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density' in y.columns:
            y = y.astype({'density':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_A_data():
    a = pd.DataFrame(list(SLR_Area.objects.all().exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density2' in y.columns:
            y = y.astype({'density2':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_AR_data():
    a = pd.DataFrame(list(SLR_Area.objects.filter(location__water = 'r').exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density2' in y.columns:
            y = y.astype({'density2':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class Slr_AL_data():
    a =  pd.DataFrame(list(SLR_Area.objects.filter(location__water = 'l').exclude(location='untersee_steckborn_siedlerm').values()))
    def format_data(y):
        t_day = pd.to_datetime('today')
        if 'density2' in y.columns:
            y = y.astype({'density2':float}, copy=False)
        y['date'] = pd.to_datetime(y['date'])
        y = y[y.date <= t_day]
        return y
    c = format_data(a)
class All_data():
    all_data = pd.concat([Slr_data.c, Mc_data.c, P_data.c])
    all_data.to_csv('dirt/static/code_data.csv', encoding='latin1')
class All_p_data():
    all_p_data = pd.concat([D_data.c, P_data.c])
class Daily():
    def __init__(self, df, names):
        self.df = df
        self.names = names
    def daily(self):
        a = self.df
        b = self.names
        e =  a['quantity'].groupby([a['date'], a['location_id'], a['length'], a['project_id']]).sum().copy()
        e = pd.DataFrame(e)
        e.reset_index(inplace=True)
        e['density'] = e['quantity']/e['length']
        e['density'] = e['density'].round(4)
        for name in b:
            n=0
            for i, row in e.iterrows():
                if e.loc[i, 'location_id'] == name:
                    n=n+1
                    e.loc[i, 'sample'] = n
        return e
class Mc_density():
    mc_density = Daily(Mc_data.c, Beaches.beachList()).daily()
class P_density():
    p_density = Daily(P_data.c, Beaches.p_beaches()).daily()
class Hdc_density():
    hdc_density = Daily(Hdc_data.c, HDC_Beaches.beachList()).daily()
class D_density():
    d_density = Daily(D_data.c, Beaches.d_beaches()).daily()
class Daily_density():
    def __init__(self, df):
        self.df = df
    def daily_density(self):
        a = self.df[['date', 'location_id', 'density','quantity', 'sample', 'project_id']].copy()
        bb = a[['date', 'location_id', 'density', 'project_id']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return x, e, bb, a
class Mc_daily():
    mc, mc_one, mc_two, mc_three = Daily_density(Mc_density.mc_density).daily_density()
class Hdc_daily():
    hdc, hdc_one, hdc_two, hdc_three = Daily_density(Hdc_density.hdc_density).daily_density()
class P_daily():
    p, p_one, p_two, p_three = Daily_density(P_density.p_density).daily_density()
class D_daily():
    d, d_one, d_two, d_three = Daily_density(D_density.d_density).daily_density()

class Slr_daily():
    slr, slr_one, slr_two, slr_three = Daily_density(Slr_density.c).daily_density()
class Slr_lake_daily():
    slr_lake, slr_lake_one, slr_lake_two, slr_lake_three = Daily_density(Slr_lake.c).daily_density()
class Slr_river_daily():
    slr_river, slr_river_one, slr_river_two, slr_river_three = Daily_density(Slr_river.c).daily_density()
class Daily_density_two():
    def __init__(self, df):
        self.df = df
    def daily_density(self):
        a = self.df[['date', 'location_id', 'density2','quantity', 'sample', 'project_id']].copy()
        bb = a[['date', 'location_id', 'density2', 'project_id']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density2'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return x, e, bb, a
class Slr_ra_density():
    slr_a_river, slr_a_river_one, slr_a_river_two, slr_a_river_three = Daily_density_two(Slr_AR_data.c).daily_density()
class Slr_la_density():
    slr_a_lake, slr_a_lake_one, slr_a_lake_two, slr_a_lake_three = Daily_density_two(Slr_AL_data.c).daily_density()
class Slr_a_density():
    slr_a, slr_a_one, slr_a_two, slr_a_three = Daily_density_two(Slr_A_data.c).daily_density()
class All_dailies():
     def __init__(self, lst):
        self.lst = lst
     def all_samples(self):
        a = []
        c = self.lst
        for v in c:
            for s in v:
                a.append(s)
        b = pd.DataFrame(a)
        return b, a
class All_ch():
    all_ch_df, all_ch_lst = All_dailies([Slr_daily.slr,Mc_daily.mc, P_daily.p]).all_samples()
    all_ch_df.to_csv('dirt/static/daily_data.csv', encoding='latin1')
class All_area():
    all_ch_dfa, all_ch_lsta = All_dailies([Slr_a_density.slr_a]).all_samples()
class All_p():
    all_p, all_p_lst = All_dailies([D_daily.d, P_daily.p]).all_samples()
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

    def material_dict():
        """
        rerturns a dict with key = code_id, value = code material
        """
        b = {}
        for code in Codes.objects.all().values():
            b.update({code['code']:code['material']})
        return b
    codes_material = material_dict()

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

    all_inventory, inv_df = top_ten_codes(All_data.all_data, codes_dict, codes_material)
    slr_inventory, inv_series = top_ten_codes(Slr_data.c, codes_dict, codes_material)
    mc_inventory, mc_inv_series = top_ten_codes(Mc_data.c, codes_dict, codes_material)
    hdc_inventory, hdc_inv_series = top_ten_codes(Hdc_data.c, codes_dict, codes_material)
    p_inventory, p_inv_series = top_ten_codes(All_p_data.all_p_data, codes_dict, codes_material)
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
        a = All_data.all_data
        b = Water_bodies.swiss
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
    site_body = water_dict(Water_bodies.swiss)
    site_body_hdc = water_dict(Water_bodies.hdc)
    site_body_p = water_dict(Water_bodies.p_w)
class Make_coordinates():
    """
    Generates the out put for a map plot on google maps API
    Includes summary information per location
    Can be passed directly to JS parser
    """
    def map_coords(plot, names, proj, water ):
        a_map = []
        a = plot['density'].groupby(plot['location_id']).mean().round(6)
#        b = names
        f = list(a.index)
        for c in f:
            g = names[c]
            e = [float(g['latitude']), float(g['longitude']), float(a[c]), g['post'], g['city'], plot[plot.location_id == c]['date'].count(), c, proj, water]
            a_map.append(e)
        return a_map
    def map_coords2(plot, names, proj, water ):
        a_map = []
        a = plot['density2'].groupby(plot['location_id']).mean().round(6)
#        b = names
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
    combined_map = coord_list([map_coords(Slr_lake_daily.slr_lake_three,  Make_cites.all_site_list, 'SLR', 'lake'),
    map_coords(Slr_river_daily.slr_river_three, Make_cites.all_site_list, 'SLR', 'river'),
    map_coords(Mc_daily.mc_three, Make_cites.all_site_list, 'MCBP', 'lake'), map_coords(P_daily.p_three, Make_cites.all_site_list, 'Precious', 'lake')])
    mc_map = coord_list([map_coords(Mc_daily.mc_three, Make_cites.all_site_list, 'MCBP', 'lake')])
    hdc_map = coord_list([map_coords(Hdc_daily.hdc_three, Make_cites.hdc_sites, 'HDC', 'river' )])
    slr_map = coord_list([map_coords2(Slr_la_density.slr_a_lake_three,  Make_cites.all_site_list, 'SLR', 'lake'),
    map_coords2(Slr_ra_density.slr_a_river_three, Make_cites.all_site_list, 'SLR', 'river')])
    p_map = coord_list([map_coords(P_daily.p_three, Make_cites.p_sites, 'Precious', 'lake' ), map_coords(D_daily.d_three, Make_cites.p_sites, 'Descente', 'river' )])

class Make_totals():
    def get_total():
        """
        aggregates the totals from the various Projects
        returns the grand total and the subtotals
        """
        slr_total = SLR_Data.objects.all().aggregate(t_total = Sum('quantity'))
        mcbp_total = AllData.objects.all().aggregate(t_total = Sum('quantity'))
        p_total = Precious.objects.all().aggregate(t_total = Sum('quantity'))
        d_total = Descente.objects.all().aggregate(t_total = Sum('quantity'))
        mc_tot = float(mcbp_total['t_total'])
        sl_tot = float(slr_total['t_total'])
        p_tot = float(p_total['t_total'])
        d_tot = float(d_total['t_total'])
        p_d_tot = p_tot +d_tot
        a = mc_tot + sl_tot + p_tot
        return a, mc_tot, sl_tot, p_tot, d_tot, p_d_tot
    a, mc_total, sl_total, p_total, d_total, p_d_total = get_total()

    def get_lakes():
        """
        gets the location_ids assigned to lake from the Make_daily Class
        combines the lists into one, returns the new list and len(list)
        and the total number of operations
        """
        b = list(Slr_lake_daily.slr_lake_two['location_id'].unique())
#        e = len(b)
        c = [Make_cites.mc_lake, Make_cites.p_lake]
        for f in c:
            for r in f:
                if r not in b:
                    b.append(r)
        g = len(b)

        return b, g
    locs_lakes, lake_locs, = get_lakes()

    def get_rivers():
        """
        gets the location_ids assigned to river from the Make_daily Class
        combines the lists into one, returns the new list and len(list)
        and the total number of operations
        """
        b = list(Slr_river_daily.slr_river_two['location_id'].unique())
        c = [Make_cites.mc_rivers, Make_cites.p_rivers]
        for f in c:
            for r in f:
                if r not in b:
                    b.append(r)
        e = len(b)
#        f = len(Slr_river_daily.slr_river)
        return b, e
    riv_locs, riv_num = get_rivers()

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
                if b[d]['water'] == 'l':
                    if a[d] not in f['lake']:
                        e = a[d]
                        f['lake'].append(e)
                elif b[d]['water'] == 'r':
                    if a[d] not in f['river']:
                        e = a[d]
                        f['river'].append(e)
        g = len(f['lake'])
        h = len(f['river'])
        return f, g, h

    lake_river, no_of_lake, no_of_river = total_lakes(Make_cites.key_list)
    mc_lake_river, mc_no_of_lake, mc_no_of_river = total_lakes(list(Make_cites.mc_site_info.keys()))
    print(Make_cites.p_sites)
#    print(Make_cites.p_sites.keys())
    def total_lakes2(c,x,z):
        """
        assigns body names to categories lake or river
        skips one record for the moment
        returns a dictionary {'lake': [ list of lake names], 'river' ...}
        returns the length of both values
        """
        a = z
        b = x

        f={'lake':[], 'river':[]}
        for d in c:
            if d != 'untersee_steckborn_siedlerm':
                if b[d]['water'] == 'l':
                    if a[d] not in f['lake']:
                        e = a[d]
                        f['lake'].append(e)
                elif b[d]['water'] == 'r':
                    if a[d] not in f['river']:
                        e = a[d]
                        f['river'].append(e)
        g = len(f['lake'])
        h = len(f['river'])
        return f, g, h
    hdc_lake_river, hdc_no_of_lake, hdc_no_of_river = total_lakes2(list(Make_cites.hdc_sites.keys()),Make_cites.hdc_sites, Make_water.site_body_hdc)
    p_lake_river, p_no_of_lake, p_no_of_river = total_lakes2(list(Make_cites.p_sites.keys()), Make_cites.p_sites, Make_water.site_body_p )
    print(p_lake_river)


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
    all_summary, number_location = make_summary(All_ch.all_ch_df)
    def make_summary2(x):

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
class Make_boxes():
    def box_plots(a):

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
        return i

    river_box = box_plots(Slr_river_daily.slr_river_two)
    lake_box = box_plots(Slr_lake_daily.slr_lake_two)
    mc_box = box_plots(Mc_daily.mc_two)
    s_box = box_plots(Slr_daily.slr_two)
    p_box = box_plots(P_daily.p_two)
    d_box = box_plots(D_daily.d_two)
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

        return i
    river_box2 = box_plots2(Slr_ra_density.slr_a_river_two)
    lake_box2 = box_plots2(Slr_la_density.slr_a_lake_two)
    s_box2 = box_plots2(Slr_a_density.slr_a_two)


class Make_logs():
    """
    creates the output to plot normal dists from density data
    """
    def lake_river_prob(name):
        e = All_ch.all_ch_df.loc[All_ch.all_ch_df.location_id.isin(Water_bodies.swiss[name])]
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

    def make_library(b,d,f ):
        h = {}
        for a in b:
            c = d[a]
            e = {c:[]}
            for t in f:
                if t['subject'] == a:
                    e[c].append(t)
            h.update(e)
        return h
    books = make_library(the_subs, sub_key, library)

def beach_litter(request):
    t_day = pd.to_datetime('today')

    ### this is for the combined data section ###
    combined_map = Make_coordinates.combined_map
    #summary_df = Make_daily.all_daily_df
    inventory = Make_codes.all_inventory
    top_ten = Make_codes.inv_df

    num_lakes = Make_totals.no_of_lake
    num_rivers = Make_totals.no_of_river
    summary, num_location = Make_totals.all_summary, Make_totals.number_location
    bodies_dict = Water_bodies.swiss
    bodies_list = Water_bodies.swiss
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

    plot_all = All_ch.all_ch_lst
    for data in plot_all:
        if type(data['density']) == str:
            print(data['location'])

    # getting the data and separating in two date groups
    summary_df_x, num_locs, loc_list  = Make_logs.lake_river_prob("Lac Léman")
    a = Make_logs.by_date(summary_df_x, "2015-11-15", "2016-11-15")
    b = Make_logs.by_date(summary_df_x, "2016-11-15", "2017-11-15")

    # get the components to sketch the distributions
    loc, scale, x_one, y_one = Make_logs.get_log_of(a)
#    print(x_one, y_one)
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
    for data in plot_mc:
        print(data['location_id'], data['density'], data['date'])

    num_samps = len(summary_df_x)


    return render(request, 'dirt/beach_litter.html', { 'mk_pers':mk_pers, 'top_ten':top_ten_table, 'top_ten_total': top_ten[:10].sum(),'all_water':Water_bodies.swiss,
    'all_cities':Make_cites.cities, 'plot_all':plot_all, 'y_one_s':len(plot_density), 'y_two_s':len(plot_mc), 'year_one':plot_density, 'year_two':plot_mc, 'combined_map':combined_map,
    'num_locs':num_location, 'dist_2016':dist_2016,'dist_2017':dist_2017 , 'num_samps':num_samps, 't_day':t_day, 'inventory':inventory, 'bodies_dict':bodies_dict, 'bodies_list':bodies_list,
    'num_lakes':num_lakes, 'num_rivers':num_rivers,'summary':summary,'box_lake':box_lake, 'box_river':box_river, 'box_mc':box_mc, 'lakes':Slr_lake_daily.slr_lake, 'rivers':Slr_river_daily.slr_river,
    'plot_mc':Mc_daily.mc, 'plot_p':P_daily.p, 'p_box':Make_boxes.p_box})

def services_home(request):
    return render(request, 'dirt/services.html')
def in_the_works(request):
    return render(request, 'dirt/intheworks.html')
def microbiology(request):

    def get_jsons_x(file_name):
        with open(os.path.join( settings.BASE_DIR, 'dirt/static/jsons/' + file_name ), 'r') as f:
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

#
        # dcitionary that relates location id to waterbody
        water_bodies = Make_cites.all_cities

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = All_ch.all_ch_df
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Daily_density(a).daily_density()

            return c_1, c_2, c_3, c_4
        # c_1 = a list of dicts in form df-record per dict
        # c_2 = a list of np.log() values for daily pcs/m
        # c_3 = a df with 'date', 'location_id', 'density'
        # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data = All_data.all_data.loc[All_data.all_data.location_id.isin(water_bodies[q])].copy()

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

        return render(request, 'dirt/search_city.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': All_ch.all_ch_lst,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')

def search_water(request):
    if 'water' in request.GET and request.GET['water']:
        q = request.GET['water']
        print(q)

        # dcitionary that relates location id to waterbody
        water_bodies = Water_bodies.swiss

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = All_ch.all_ch_df
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Daily_density(a).daily_density()

            return c_1, c_2, c_3, c_4

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data =All_data.all_data.loc[All_data.all_data.location_id.isin(water_bodies[q])].copy()

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


        return render(request, 'dirt/search_water.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': All_ch.all_ch_lst,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')

def search_SLR(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        print(q)

        # dcitionary that relates location id to waterbody
        water_bodies = Make_cites.all_cities

        # this gets the data for the report
        def get_daily_values(criteria):
            # gets the values associated with the user choice
            # sets the date and time stamp
            # calls Make_daily to sort and make different lists\
            a = Slr_a_density.slr_a_three
            a['date'] = pd.to_datetime(a['date'])
            a = a.loc[a.location_id.isin(water_bodies[criteria])]
            c_1, c_2, c_3, c_4 = Daily_density_two(a).daily_density()

            return c_1, c_2, c_3, c_4
        # c_1 = a list of dicts in form df-record per dict
        # c_2 = a list of np.log() values for daily pcs/m
        # c_3 = a df with 'date', 'location_id', 'density'
        # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

        c_1, c_2, c_3, c_4 = get_daily_values(q)


        summary, num_locs= Make_totals.make_summary2(c_4)

        map_data = Make_coordinates.coord_list([Make_coordinates.map_coords2(c_3, Make_cites.all_site_list, 'Combined', q)])
        code_data = Slr_data.c.loc[Slr_data.c.location_id.isin(water_bodies[q])].copy()
        print(code_data.columns)

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

        return render(request, 'dirt/search_slr.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
        'plot_density':c_1,'plot_all': Slr_a_density.slr_a,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density2']) + 10, 'inventory':total_inventory,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

    else:
        return HttpResponse('Please submit a search term')



def search_MCBP(request):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']
            print('break!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(q)

            # dcitionary that relates location id to waterbody
            water_bodies = Make_cites.all_mc_cities

            # this gets the data for the report
            def get_daily_values(criteria):
                # gets the values associated with the user choice
                # sets the date and time stamp
                # calls Make_daily to sort and make different lists\
                a = Mc_daily.mc_three
                a['date'] = pd.to_datetime(a['date'])
                a = a.loc[a.location_id.isin(water_bodies[criteria])]
                c_1, c_2, c_3, c_4 = Daily_density(a).daily_density()
                return c_1, c_2, c_3, c_4
            # c_1 = a list of dicts in form df-record per dict
            # c_2 = a list of np.log() values for daily pcs/m
            # c_3 = a df with 'date', 'location_id', 'density'
            # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

            c_1, c_2, c_3, c_4 = get_daily_values(q)


            summary, num_locs= Make_totals.make_summary(c_4)

            map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.mc_site_info, 'MCBP', q)])
            code_data = Mc_data.c.loc[Mc_data.c.location_id.isin(water_bodies[q])].copy()

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

            #color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

            return render(request, 'dirt/search_MCBP.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
            'plot_density':c_1,'plot_all': Mc_daily.mc,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
            'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

        else:
            return HttpResponse('Please submit a search term')



def slr_home(request):

    #slr_locs = SLR_Beaches.beachList()
    #slr_beaches = SLR_Beaches.objects.all().values()


    summary, number_locations = Make_totals.make_summary2(Slr_A_data.c)
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
    cities = city_list(Slr_a_density.slr_a_three)

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


    def locs_and_samples():
        a =  Slr_A_data.c.groupby('location_id')
        b = a.agg({'density2':np.mean, 'sample':max})
        b.reset_index(inplace=True)
        c = b.to_dict('records')
        return c

    return render(request, 'dirt/slr.html', {'books':books, 'num_lakes':Make_totals.no_of_lake, 'num_rivers':Make_totals.no_of_river,
    'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Slr_a_density.slr_a,
    'map_points':map_points, 'slr_cities': cities,'box_plot': Make_boxes.s_box2,'lakes':Slr_la_density.slr_a_lake, 'rivers':Slr_ra_density.slr_a_river, 'box_lake':Make_boxes.lake_box2, 'box_river':Make_boxes.river_box2,
    'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_slr_cities, 'slr_river':Make_cites.slr_rivers,
    'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities})

def mcbp_home(request):
        #slr_locs = Beaches.beachList()
        slr_beaches = Beaches.objects.filter(project = 'MCBP').values()
        # codes = Codes.objects.all()

        summary, number_locations = Make_totals.make_summary(Mc_density.mc_density.loc[Mc_density.mc_density.project_id == 'MCBP'])
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

        # color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        def locs_and_samples():
            a =  Mc_density.mc_density.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        return render(request, 'dirt/mcbp.html', {'books':books, 'num_lakes':Make_totals.mc_no_of_lake, 'num_rivers':Make_totals.mc_no_of_river,
        'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Mc_daily.mc,
        'map_points':map_points, 'slr_cities': cities,'box_plot':Make_boxes.mc_box, 'lakes':Slr_lake_daily.slr_lake, 'rivers':Slr_river_daily.slr_river, 'box_lake':Make_boxes.lake_box, 'box_river':Make_boxes.river_box,
        'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_mc_cities, 'slr_river':Make_cites.mc_rivers,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.mc_cities})


def hdc_home(request):

        slr_beaches = HDC_Beaches.objects.all().values()
        # codes = Codes.objects.all()

        summary, number_locations = Make_totals.make_summary(Hdc_density.hdc_density)
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


        def locs_and_samples():
            a =  Hdc_density.hdc_density.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        return render(request, 'dirt/hdc.html', {'books':books, 'num_lakes':Make_totals.hdc_no_of_lake, 'num_rivers':Make_totals.hdc_no_of_river,
        'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': Hdc_daily.hdc,
        'map_points':map_points, 'slr_cities': cities,'box_plot':Make_boxes.mc_box, 'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_hdc_cities, 'slr_river':Make_cites.hdc_rivers,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities})

def search_hdc(request):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']

            # dcitionary that relates location id to waterbody
            water_bodies = Make_cites.all_hdc_cities

            # this gets the data for the report
            def get_daily_values(criteria):
                # gets the values associated with the user choice
                # sets the date and time stamp
                # calls Make_daily to sort and make different lists\
                a = Hdc_daily.hdc_three
                a['date'] = pd.to_datetime(a['date'])
                a = a.loc[a.location_id.isin(water_bodies[criteria])]
                c_1, c_2, c_3, c_4 = Daily_density(a).daily_density()

                return c_1, c_2, c_3, c_4
            # c_1 = a list of dicts in form df-record per dict
            # c_2 = a list of np.log() values for daily pcs/m
            # c_3 = a df with 'date', 'location_id', 'density'
            # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

            c_1, c_2, c_3, c_4 = get_daily_values(q)


            summary, num_locs= Make_totals.make_summary(c_4)

            map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.hdc_sites, 'HDC', q)])
            code_data = Hdc_data.c.loc[Hdc_data.c.location_id.isin(water_bodies[q])].copy()

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


            return render(request, 'dirt/search_hdc.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
            'plot_density':c_1,'plot_all': Hdc_daily.hdc,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
            'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

        else:
            return HttpResponse('Please submit a search term')


def precious(request):
        #slr_locs = Beaches.beachList()
        slr_beaches = Make_cites.p_all
        # codes = Codes.objects.all()
        p_d_density = pd.concat([P_density.p_density, D_density.d_density])

        summary, number_locations = Make_totals.make_summary(p_d_density)
        map_points = Make_coordinates.p_map
        inventory = Make_codes.p_inventory
        mk_pers = Make_percents(Make_codes.p_inv_series, Make_codes.codes_material).get_percents()

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

        # color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

        def locs_and_samples():
            a =  p_d_density.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c

        return render(request, 'dirt/precious.html', {'books':books, 'num_lakes':Make_totals.p_no_of_lake, 'num_rivers':Make_totals.p_no_of_river,
        'num_locs':number_locations, 'top_ten':top_ten_table, 'summary':summary, 'mk_pers':mk_pers, 'plot_density': All_p.all_p_lst,
        'map_points':map_points, 'slr_cities': cities,'box_plot':Make_boxes.p_box, 'lakes':P_daily.p, 'rivers':D_daily.d, 'box_lake':Make_boxes.d_box,
        'inventory':inventory, 'locs_samples':locs_and_samples(), 'city_locs':Make_cites.all_p_cities, 'slr_river':Make_cites.p_rivers,
        'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities})
def search_precious(request):
        if 'q' in request.GET and request.GET['q']:
            q = request.GET['q']

            # dcitionary that relates location id to waterbody
            water_bodies = Make_cites.all_p_cities

            # this gets the data for the report
            def get_daily_values(criteria):
                # gets the values associated with the user choice
                # sets the date and time stamp
                # calls Make_daily to sort and make different lists\
                a = pd.concat([P_daily.p_three, D_daily.d_three])
                a['date'] = pd.to_datetime(a['date'])
                a = a.loc[a.location_id.isin(water_bodies[criteria])]
                c_1, c_2, c_3, c_4 = Daily_density(a).daily_density()

                return c_1, c_2, c_3, c_4
            # c_1 = a list of dicts in form df-record per dict
            # c_2 = a list of np.log() values for daily pcs/m
            # c_3 = a df with 'date', 'location_id', 'density'
            # c_4 = a df with 'date', 'location_id', 'density','quantity', 'sample'

            c_1, c_2, c_3, c_4 = get_daily_values(q)


            summary, num_locs= Make_totals.make_summary(c_4)

            map_data = Make_coordinates.coord_list([Make_coordinates.map_coords(c_3, Make_cites.p_sites, 'Precious', q)])
            print(map_data)
            code_data = All_p_data.all_p_data.loc[All_p_data.all_p_data.location_id.isin(water_bodies[q])].copy()

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


            return render(request, 'dirt/search_precious.html', {'city':q, 'city_top_ten':t_ten, 'summary':summary,  'num_locs':num_locs, 'mk_pers':mk_pers,
            'plot_density':c_1,'plot_all': All_p.all_p_lst,'map_points':map_data, 'locs_samples':locs_and_samples(), 'ceiling':max(c_4['density']) + 10, 'inventory':total_inventory,
            'all_water':Water_bodies.swiss, 'all_cities':Make_cites.cities,})

        else:
            return HttpResponse('Please submit a search term')
