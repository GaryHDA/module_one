# beaches/dirt/views.py

from django.db import models
from django.db.models import Sum, Avg, Max, Min
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from dirt.models import SLR_Data, SLR_Density, SLR_Beaches, Beaches, Codes, All_Data, References, SUBJECT_CHOICES
from django.contrib.auth.models import User
import datetime
import pandas as pd
import math
import numpy as np
from scipy.stats import norm
import scipy.stats
from datetime import date

def index(request):
    slr_data = SLR_Data.objects.all().values()
    slr_density = SLR_Density.objects.all().values()
    slr_locs = SLR_Beaches.beachList()
    slr_beaches = SLR_Beaches.objects.all().values()
    river_dens = SLR_Density.objects.filter(location__water = 'river').values()
    lake_dens = SLR_Density.objects.filter(location__water = 'lake').values()

    mcbp_density = All_Data.objects.all().values()
    mc_beaches = Beaches.beachList()
    mc_locs = Beaches.objects.all().values()

    slr_total = SLR_Data.objects.all().aggregate(t_total = Sum('quantity'))
    mcbp_total = All_Data.objects.all().aggregate(t_total = Sum('quantity'))

    mc_tot = float(mcbp_total['t_total'])
    sl_tot = float(slr_total['t_total'])

    t_day = pd.to_datetime('today')
    #
    # def date_string_y(x):
    #     t = x.strftime('%Y-%m-%d')
    #     return t
    def make_df(y):
        a = list(y)
        b = pd.DataFrame(a)
        return [a, b]
    def format_data(y):
        a = y.columns
        if 'quantity' in a:
            y = y.astype({'quantity':float}, copy=False)
        if 'density' in a:
            y = y.astype({'density':float}, copy=False)
        if 'date' in a:
            y['date'] = pd.to_datetime(y['date'])
            y = y[y.date < t_day]
        if 'sample' in a:
            y = y.astype({'sample':float}, copy=False)
        if 'length' in a:
            y = y.astype({'length':float}, copy=False)
        return y

    df0 = format_data(make_df(slr_density)[1])
    dfMCBP = format_data(make_df(mcbp_density)[1])
    dfR = format_data(make_df(river_dens)[1])
    dfL = format_data(make_df(lake_dens)[1])

    def mcbp_daily():
        a = dfMCBP.copy()
        d =  a['quantity'].groupby([a['date'], a['location_id'], a['length']]).sum()
        e = pd.DataFrame(d)
        e.reset_index(inplace=True)
        e = e[e.date > min(e.date)]
        e['density'] = e['quantity']/e['length']
        e['density'] = e['density'].round(4)
        for name in mc_beaches:
            n=0
            for i, row in e.iterrows():
                if e.loc[i, 'location_id'] == name:
                    n=n+1
                    e.loc[i, 'sample'] = n
        return e
    mc = mcbp_daily()

    def daily_density(df):
        a = df[['date', 'location_id', 'density', 'sample']].copy()
        bb = a[['date', 'location_id', 'density']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return [x, e, bb, a]
    plot_density = daily_density(df0)
    plot_mc = daily_density(mc)
    slr_hist = plot_density[1]
    mc_hist = plot_mc[1]
    # lakes = daily_density(dfL)
    # rivers = daily_density(dfR)

    plot_list = []
    hist_list = []
    def this_list(n, j):
        for a in n:
            j.append(a)
    this_list(slr_hist, hist_list)
    this_list(mc_hist, hist_list)
    this_list(plot_mc[0], plot_list)
    this_list(plot_density[0], plot_list)
    num_samps = len(plot_list)


    return render(request, 'dirt/index.html', { 'plot_list':plot_list, 'hist_list':hist_list, 'num_samps':num_samps, 't_day':t_day})


# 'plot_mc':plot_mc[0], 'plot_density':plot_density[0],


def services_home(request):
    return render(request, 'dirt/services.html')
# def finance_home(request):
#     return render(request, 'dirt/pension.html')
# def module_one(request):
    # slr_d = SLR_Density.objects.all().values()
    # mcbp = All_Data.objects.all().values()


def search_SLR(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        city_values = SLR_Data.objects.filter(location__city = q).values()
        city_densities = SLR_Density.objects.filter(location__city = q).values()
        codes = Codes.objects.all().values()
        beaches = SLR_Beaches.objects.all().values()
        all_densities = SLR_Density.objects.all().values()

        t_day = pd.to_datetime('today')

        # def date_string_y(x):
        #     t = x.strftime('%Y-%m-%d')
        #     return t
        def make_df(y):
            a = list(y)
            b = pd.DataFrame(a)
            return [a, b]
        dfX = make_df(city_values)
        dfY = make_df(city_densities)
        dfZ = make_df(all_densities)



        def format_data(x):
            x = x.astype({'density':float, 'quantity':float}, copy=False)
            x['date'] = pd.to_datetime(x['date'])
            r = x[x.date < t_day]
            return r
        df = format_data(dfX[1])
        df0 = format_data(dfY[1])
        df1 = format_data(dfZ[1])

        # get the location names of the beaches in the city
        def get_beaches(y):
            a = []
            b = list(y)
            for x in b:
                if x['location_id'] not in a:
                    a.append(x['location_id'])
            return a
        beaches_x = get_beaches(city_densities)

        def city_list(city_query):
            b = []
            a = list(city_query)
            for x in a:
                if x['city'] not in b:
                    b.append(x['city'])
            return b
        cities = city_list(beaches)

        def make_summary():
            f = df0.describe()['density']
            num_samps = f['count']
            stan_dev = f['std'].round(2)
            dens_min = f['min'].round(4)
            dens_max = f['max'].round(2)
            two_five = f['25%'].round(2)
            seven_five = f['75%'].round(2)
            average = f['mean'].round(2)
            first_sample = min(df0['date'])
            last_sample = max(df0['date'])
            total = df0['quantity'].sum()
            iqr = seven_five - two_five
            x = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
            'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
            return x
        summary = make_summary()

        def daily_density(df):
            a = df[['date', 'location_id', 'density', 'sample']].copy()
            bb = a[['date', 'location_id', 'density']].copy()
            a['date'] = a['date'].dt.strftime("%Y-%m-%d")
            x = a.to_dict(orient='records')
            z = max(df['density']) + 1

            return [x, bb, a, z]

        densities = daily_density(df0)
        all_values = daily_density(df1)
        # pass to response
        plot_density = densities[0]
        plot_all = all_values[0]
        b_plot = densities[1]

        def box_plots(a):
            b = a.copy()
            b.set_index('date', inplace=True)
            c = b.groupby([b.index.year, b.index.month])
            d = list(c)
            f = []
            for g,h in enumerate(d):
                f.append(d[g][1])
            return f
        bx_plot = box_plots(b_plot)

        def boxes(a):
            f = []
            months = ['Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017', 'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']
            for b, c in enumerate(a):
                d = a[b]
                d['density'] = d['density'].astype(float)
                e = list(d['density'])
                g = sorted(e)
                h = [min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), g[-1]]
                f.append(h)
            return [f, months]

        box_plot_s = boxes(bx_plot)

        # pass to response
        box_plot = box_plot_s[0]
        box_cats = box_plot_s[1]

        def map_coords(plot, names ):
            a_map = []
            a = plot['density'].groupby(plot['location_id']).mean().round(6)
            a = a.astype(float)
            b = list(names)
            for c in b:
                if c['location'] in a.index:
                    c['density'] = a[c['location']]
                    if 'density' in c:
                            e = [float(c['latitude']), float(c['longitude']), float(c['density']), c['post'], c['city'], plot[plot.location_id == c['location']]['sample'].max(), c['location']]
                            a_map.append(e)
            return [a_map, b]

        map_data = map_coords(densities[2], beaches)
        map_points = map_data[0]

        def top_ten_codes():
            a = df['quantity'].groupby(df['code_id']).sum()
            b = a.sort_values(ascending=False)
            c = b[:10]
            d = list(c.index)
            f = []
            for g in d:
                for h in codes:
                    if h['code'] == g:
                        f.append({'code':g, 'description':h['description'], 'total':c[g]})
            return [a, f]
        city_top_ten = top_ten_codes()[1]


        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']
        def sources():
            a = top_ten_codes()[0]
            b = a.to_dict()
            c = b.keys()
            d = []
            for g in codes:
                if g['code'] in c:
                    d.append({'code':g['code'], 'source':g['source'], 'total':b[g['code']]})
            h = pd.DataFrame(d)
            i = h['total'].groupby(h['source']).sum()
            l = sum(i)
            j = []
            for n, r in enumerate(i.index):
                f = (i[n]/l)*100
                k = {'source':f, 'name':r, 'color':color[n]}
                j.append(k)
            return j
        sources_as = sources()

        def locs_and_samples():
            a = df0.groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c
        def percentile_ranking_locations():
            a = df0['density'].mean()
            b = list(df1['density'])
            b.sort()
            c = scipy.stats.percentileofscore(b, a)
            return [c, a]
        beach_rank = percentile_ranking_locations()

        def percentile_ranking_cities():
            city_aves = []
            for s in cities:
                v = SLR_Density.objects.filter(location__city = s).aggregate(ave = Avg('density'))
                u = v['ave']
                if u != None:
                    city_aves.append(u)
            city_aves.sort()
            t = scipy.stats.percentileofscore(city_aves, beach_rank[1])
            return [city_aves, t]
        city_rank = percentile_ranking_cities()[1]

        def inventory(a):
            b =pd.DataFrame(a['quantity'].groupby([a['code_id'], a['location_id']]).sum())
            bindex = []
            for c in b.index.get_level_values(0):
                if c not in bindex:
                    bindex.append(c)
            inv = []
            for x in bindex:
                f = codes.filter(code=x).values()[0]['description']
                g = b.loc[x]
                h = {'code':x, 'description':f, 'total':g['quantity'].sum()}
                inv.append(h)
            return inv
        total_inventory = inventory(df)

        return render(request, 'dirt/search_SLR.html', {'city':q, 'beaches_x':beaches_x, 'sources_as':sources_as, 'city_top_ten':city_top_ten, 'summary':summary,
        'plot_density':plot_density,'plot_all':plot_all,'map_points':map_data[0], 'box_plot': box_plot, 'box_cats':box_cats, 'bx_plot':bx_plot,
        'locs_samples':locs_and_samples(), 'city_rank':city_rank, 'beach_rank':beach_rank[0], 'ceiling':densities[3], 'inventory':total_inventory})

    else:
        return HttpResponse('Please submit a search term')

def search_MCBP(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        city_values = All_Data.objects.filter(location__city = q).values()
        codes = Codes.objects.all().values()
        beaches = Beaches.objects.all().values()
        all_densities = All_Data.objects.all().values()
        beaches_list = Beaches.beachList()

        t_day = pd.to_datetime('today')

        # def date_string_y(x):
        #     t = x.strftime('%Y-%m-%d')
        #     return t
        def make_df(y):
            a = list(y)
            b = pd.DataFrame(a)
            return [a, b]
        def format_data(y):
            a = y.columns
            if 'quantity' in a:
                y = y.astype({'quantity':float}, copy=False)
            if 'density' in a:
                y = y.astype({'density':float}, copy=False)
            if 'date' in a:
                y['date'] = pd.to_datetime(y['date'])
                y = y[y.date < t_day]
            if 'sample' in a:
                y = y.astype({'sample':float}, copy=False)
            if 'length' in a:
                y = y.astype({'length':float}, copy=False)
            return y
        dfCity = format_data(make_df(city_values)[1])
        dfMC = format_data(make_df(all_densities)[1])

        def mcbp_daily(x):
            a = x.copy()
            d =  a['quantity'].groupby([a['date'], a['location_id'], a['length']]).sum()
            e = pd.DataFrame(d)
            e.reset_index(inplace=True)
            # e = e[e.date > min(e.date)]
            e['density'] = e['quantity']/e['length']
            e['density'] = e['density'].round(4)
            for name in beaches_list:
                n=0
                for i, row in e.iterrows():
                    if e.loc[i, 'location_id'] == name:
                        n=n+1
                        e.loc[i, 'sample'] = n
            return e
        def daily_density(df):
            a = df[['date', 'location_id', 'density', 'sample']].copy()
            bb = a[['date', 'location_id', 'density']].copy()
            a['date'] = a['date'].dt.strftime("%Y-%m-%d")
            x = a.to_dict(orient='records')
            b = list(a['density'])
            c = sorted(b)
            z = max(df['density']) + 1
            return [x,bb, a, c, b,z]
        city_daily = daily_density(mcbp_daily(dfCity))
        mc_daily = daily_density(mcbp_daily(dfMC))

        # get the location names of the beaches in the city
        def get_beaches(y):
            a = []
            b = list(y)
            for x in b:
                if x['location_id'] not in a:
                    a.append(x['location_id'])
            return a
        beaches_x = get_beaches(city_values)

        def city_list(city_query):
            b = []
            a = list(city_query)
            for x in a:
                if x['city'] not in b:
                    b.append(x['city'])
            return b
        cities = city_list(beaches)

        def make_summary(x, y):
            f = x.describe()['density']
            num_samps = f['count']
            stan_dev = f['std'].round(2)
            dens_min = f['min'].round(4)
            dens_max = f['max'].round(2)
            two_five = f['25%'].round(2)
            seven_five = f['75%'].round(2)
            average = f['mean'].round(2)
            first_sample = min(y['date'])
            last_sample = max(y['date'])
            total = y['quantity'].sum()
            iqr = seven_five - two_five
            x = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
            'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
            return x
        summary = make_summary(city_daily[2], dfCity)

        def box_plots(a):
            b = a.copy()
            b.set_index('date', inplace=True)
            c = b.groupby([b.index.year, b.index.month])
            d = list(c)
            f = []
            for g,h in enumerate(d):
                f.append(d[g][1])
            return f
        bx_plot = box_plots(city_daily[1])

        box_cats = ['Nov-2015', 'Dec-2015', 'Jan-2016', 'Feb-2016', 'Mar-2016', 'Apr-2016', 'May-2016',
        'Jun-2016', 'Jul-2016', 'Aug-2016', 'Sep-2016', 'Oct-2016', 'Nov-2016', 'Dec-2016', 'Jan-2017',
        'Feb-2017', 'Mar-2017','Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017',
        'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']

        def boxes(a):
            f = []
            months = box_cats
            for b, c in enumerate(a):
                d = a[b]
                d['density'] = d['density'].astype(float)
                e = list(d['density'])
                g = sorted(e)
                h = [min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), g[-1]]
                f.append(h)
            return [f, months]

        box_plot_s = boxes(bx_plot)

        # pass to response
        box_plot = box_plot_s[0]
        box_cats = box_plot_s[1]

        def map_coords(plot, names ):
            a_map = []
            a = plot['density'].groupby(plot['location_id']).mean().round(6)
            a = a.astype(float)
            b = list(names)
            for c in b:
                if c['location'] in a.index:
                    c['density'] = a[c['location']]
                    if 'density' in c:
                            e = [float(c['latitude']), float(c['longitude']), float(c['density'].round(2)), c['post'], c['city'], plot[plot.location_id == c['location']]['sample'].max(), c['location']]
                            a_map.append(e)
            return [a_map, b]

        map_data = map_coords(city_daily[2], beaches)
        map_points = map_data[0]

        def top_ten_codes(x):
            a = x['quantity'].groupby(x['code_id']).sum()
            b = a.sort_values(ascending=False)
            c = b[:10]
            d = list(c.index)
            f = []
            for g in d:
                for h in codes:
                    if h['code'] == g:
                        f.append({'code':g, 'description':h['description'], 'total':c[g]})
            return [a, f]
        the_top = top_ten_codes(dfCity)
        city_top_ten =the_top[1]


        color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']
        def sources():
            a = the_top[0]
            b = a.to_dict()
            c = b.keys()
            d = []
            for g in codes:
                if g['code'] in c:
                    d.append({'code':g['code'], 'source':g['source'], 'total':b[g['code']]})
            h = pd.DataFrame(d)
            i = h['total'].groupby(h['source']).sum()
            l = sum(i)
            j = []
            for n, r in enumerate(i.index):
                f = (i[n]/l)*100
                k = {'source':f, 'name':r, 'color':color[n]}
                j.append(k)
            return j
        sources_as = sources()

        def locs_and_samples():
            a = city_daily[2].groupby('location_id')
            b = a.agg({'density':np.mean, 'sample':max})
            b.reset_index(inplace=True)
            c = b.to_dict('records')
            return c
        def percentile_ranking_locations():
            a = city_daily[1]['density'].mean()
            b = mc_daily[4]
            b.sort()
            c = scipy.stats.percentileofscore(b, a)
            return [c, a]
        beach_rank = percentile_ranking_locations()

        def inventory(a):
            b =pd.DataFrame(a['quantity'].groupby([a['code_id'], a['location_id']]).sum())
            d = b[b.quantity > 0]
            bindex = []
            for c in d.index.get_level_values(0):
                if c not in bindex:
                    bindex.append(c)
            inv = []
            for x in bindex:
                f = codes.filter(code=x).values()[0]['description']
                g = b.loc[x]
                h = {'code':x, 'description':f, 'total':g['quantity'].sum()}
                inv.append(h)
            return inv
        total_inventory = inventory(dfCity)

        return render(request, 'dirt/search_MCBP.html', {'city':q, 'beaches_x':beaches_x, 'sources_as':sources_as, 'city_top_ten':city_top_ten, 'summary':summary,
        'plot_density':city_daily[0],'plot_all':mc_daily[0],'map_points':map_data[0], 'box_plot': box_plot, 'box_cats':box_cats, 'bx_plot':bx_plot,
        'locs_samples':locs_and_samples(), 'beach_rank':beach_rank[0], 'ceiling':city_daily[5], 'inventory':total_inventory})

    else:
        return HttpResponse('Please submit a search term')


def beach_litter(request):
    slr_data = SLR_Data.objects.all().values()
    slr_density = SLR_Density.objects.all().values()
    slr_locs = SLR_Beaches.beachList()
    slr_beaches = SLR_Beaches.objects.all().values()
    river_dens = SLR_Density.objects.filter(location__water = 'river').values()
    lake_dens = SLR_Density.objects.filter(location__water = 'lake').values()

    mcbp_density = All_Data.objects.all().values()
    mc_beaches = Beaches.beachList()
    mc_locs = Beaches.objects.all().values()

    slr_total = SLR_Data.objects.all().aggregate(t_total = Sum('quantity'))
    mcbp_total = All_Data.objects.all().aggregate(t_total = Sum('quantity'))

    mc_tot = float(mcbp_total['t_total'])
    sl_tot = float(slr_total['t_total'])

    t_day = pd.to_datetime('today')
    #
    # def date_string_y(x):
    #     t = x.strftime('%Y-%m-%d')
    #     return t
    def make_df(y):
        a = list(y)
        b = pd.DataFrame(a)
        return [a, b]
    def format_data(y):
        a = y.columns
        if 'quantity' in a:
            y = y.astype({'quantity':float}, copy=False)
        if 'density' in a:
            y = y.astype({'density':float}, copy=False)
        if 'date' in a:
            y['date'] = pd.to_datetime(y['date'])
            y = y[y.date < t_day]
        if 'sample' in a:
            y = y.astype({'sample':float}, copy=False)
        if 'length' in a:
            y = y.astype({'length':float}, copy=False)
        return y

    df0 = format_data(make_df(slr_density)[1])
    dfMCBP = format_data(make_df(mcbp_density)[1])
    dfR = format_data(make_df(river_dens)[1])
    dfL = format_data(make_df(lake_dens)[1])

    def mcbp_daily():
        a = dfMCBP.copy()
        d =  a['quantity'].groupby([a['date'], a['location_id'], a['length']]).sum()
        e = pd.DataFrame(d)
        e.reset_index(inplace=True)
        e = e[e.date > min(e.date)]
        e['density'] = e['quantity']/e['length']
        e['density'] = e['density'].round(4)
        for name in mc_beaches:
            n=0
            for i, row in e.iterrows():
                if e.loc[i, 'location_id'] == name:
                    n=n+1
                    e.loc[i, 'sample'] = n
        return e
    mc = mcbp_daily()

    def daily_density(df):
        a = df[['date', 'location_id', 'density', 'sample']].copy()
        bb = a[['date', 'location_id', 'density']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]
        return [x, e, bb, a]
    plot_density = daily_density(df0)
    plot_mc = daily_density(mc)
    slr_hist = plot_density[1]
    mc_hist = plot_mc[1]
    lakes = daily_density(dfL)
    rivers = daily_density(dfR)

    def box_plots(a):
        a.set_index('date', inplace=True)
        b = a.copy()
        c = b.groupby([b.index.year, b.index.month])
        d = list(c)
        f = []
        for g,h in enumerate(d):
            f.append(d[g][1])
        return f
    river_box = box_plots(rivers[2])
    lake_box = box_plots(lakes[2])
    mc_box = box_plots(plot_mc[2])

    box_cats = ['Nov-2015', 'Dec-2015', 'Jan-2016', 'Feb-2016', 'Mar-2016', 'Apr-2016', 'May-2016',
    'Jun-2016', 'Jul-2016', 'Aug-2016', 'Sep-2016', 'Oct-2016', 'Nov-2016', 'Dec-2016', 'Jan-2017',
    'Feb-2017', 'Mar-2017','Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017',
    'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']


    def boxes(a,l):
        f = []
        months = ['Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017', 'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']
        for b, c in enumerate(a):
            d = a[b]
            d['density'] = d['density'].astype(float)
            e = list(d['density'])
            g = sorted(e)
            if len(g) == 1:
                g=g[0]
                if l == 'SLR':
                    h = [months[b], g, g, g, g, g]
                if l == 'MCBP':
                    h = [box_cats[b], g, g, g, g, g]
            elif len(g) >= 4:
                if l == 'SLR':
                    h = [months[b],min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), max(g)]
                elif l == 'MCBP':
                    h = [box_cats[b],min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), max(g)]
            elif len(g) == 3:
                if l == 'SLR':
                    h = [months[b],g[0], (g[0]+g[1])/2, np.median(g), (g[1]+g[2])/2 , g[2]]
                elif l == 'MCBP':
                    h = [box_cats[b],g[0], (g[0]+g[1])/2, np.median(g), (g[1]+g[2])/2 , g[2]]
            elif len(g) == 2:
                if l == 'SLR':
                    h = [months[b],g[0], g[0], np.median(g), g[1] , g[1]]
                elif l == 'MCBP':
                    h = [box_cats[b],g[0], g[0], np.median(g), g[1], g[1]]
            f.append(h)
        return [f, months]

    box_lake = boxes(lake_box, 'SLR')
    box_river = boxes(river_box, 'SLR')
    box_mc = boxes(mc_box, 'MCBP')

    def map_coords(plot, names, proj, water):
        a_map = []
        a = plot['density'].groupby(plot['location_id']).mean().round(6)
        b = list(names)
        for c in b:
            if c['location'] in a.index:
                c['density'] = a[c['location']]
                if 'density' in c:
                        e = [float(c['latitude']), float(c['longitude']), float(c['density'].round(3)), c['post'], c['city'], plot[plot.location_id == c['location']]['sample'].max(), c['location'], proj, water]
                        a_map.append(e)
        return a_map

    lake = map_coords(lakes[3], slr_beaches, 'SLR', 'lake')
    river = map_coords(rivers[3], slr_beaches, 'SLR', 'river')
    mc_map = map_coords(plot_mc[3], mc_locs, 'MCBP', 'lake')

    def coord_list(b):
        a = []
        for v in b:
            for s in v:
                a.append(s)
        return(a)
    combined_map = coord_list([lake, river, mc_map])
    combined_data = coord_list([plot_mc[0], plot_density[0]])

    summary_df = pd.DataFrame(combined_data)

    def make_summary(x):
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
        total = sl_tot + mc_tot
        iqr = seven_five - two_five
        q = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
        'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
        return q

    summary = make_summary(summary_df)


    return render(request, 'dirt/beach_litter.html', {'plot_density':plot_density[0],'plot_mc':plot_mc[0],
    'slr_hist':slr_hist, 'mc_hist':mc_hist, 'lakes':lakes[0], 'rivers':rivers[0], 'box_lake':box_lake[0], 'box_river':box_river[0],
    'box_cats':box_cats, 'box_mc':box_mc[0], 'combined_map': combined_map, 'summary':summary})


def slr_home(request):
    slr_data = SLR_Data.objects.all().values()
    slr_density = SLR_Density.objects.all().values()
    slr_locs = SLR_Beaches.beachList()
    slr_beaches = SLR_Beaches.objects.all().values()
    river_dens = SLR_Density.objects.filter(location__water = 'river').values()
    lake_dens = SLR_Density.objects.filter(location__water = 'lake').values()

    codes = Codes.objects.all()

    t_day = pd.to_datetime('today')
    # def date_string_y(x):
    #     t = x.strftime('%Y-%m-%d')
    #     return t

    def make_df(y):
        a = list(y)
        b = pd.DataFrame(a)
        return [a, b]
    df = make_df(slr_data)[1]


    def format_data(y):
        a = y.columns
        if 'quantity' in a:
            y = y.astype({'quantity':float}, copy=False)
        if 'density' in a:
            y = y.astype({'density':float}, copy=False)
        if 'date' in a:
            y['date'] = pd.to_datetime(y['date'])
            y = y[y.date < t_day]
        if 'sample' in a:
            y = y.astype({'sample':float}, copy=False)
        if 'length' in a:
            y = y.astype({'length':float}, copy=False)
        return y

    df0 =  format_data(make_df(slr_density)[1])
    dfR = format_data(make_df(river_dens)[1])
    dfL = format_data(make_df(lake_dens)[1])

    def city_list(city_query):
        b = []
        a = list(city_query)
        for x in a:
            if x['city'] not in b:
                b.append(x['city'])
        b=sorted(b)
        return b
    cities = city_list(slr_beaches)

    def make_summary():
        f = df0.describe()['density']
        num_samps = f['count']
        stan_dev = f['std'].round(2)
        dens_min = f['min'].round(4)
        dens_max = f['max'].round(2)
        two_five = f['25%'].round(2)
        seven_five = f['75%'].round(2)
        average = f['mean'].round(2)
        first_sample = min(df0['date'])
        last_sample = max(df0['date'])
        total = df0['quantity'].sum()
        iqr = seven_five - two_five
        x = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
        'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
        return x

    summary = make_summary()

    def daily_density(df):
        a = df[['date', 'location_id', 'density', 'sample']].copy()
        bb = a[['date', 'location_id', 'density']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')

        return [x, bb, a]
    plot_density = daily_density(df0)
    b_plot = plot_density[1]
    lakes = daily_density(dfL)
    rivers = daily_density(dfR)

    def box_plots(a):
        a.set_index('date', inplace=True)
        b = a.copy()
        c = b.groupby([b.index.year, b.index.month])
        d = list(c)
        f = []
        for g,h in enumerate(d):
            f.append(d[g][1])
        return f
    bx_plot = box_plots(b_plot)
    river_box = box_plots(rivers[1])
    lake_box = box_plots(lakes[1])

    def boxes(a):
        f = []
        months = ['Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017', 'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']
        for b, c in enumerate(a):
            d = a[b]
            d['density'] = d['density'].astype(float)
            e = list(d['density'])
            g = sorted(e)
            h = [min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), g[-1]]
            f.append(h)
        return [f, months]

    box_plot_s = boxes(bx_plot)
    box_plot = box_plot_s[0]
    box_cats = box_plot_s[1]
    box_lake = boxes(lake_box)
    box_river = boxes(river_box)


    def map_coords(plot, names ):
        a_map = []
        a = plot['density'].groupby(plot['location_id']).mean().round(6)
        a = a.astype(float)
        b = list(names)
        for c in b:
            if c['location'] in a.index:
                c['density'] = a[c['location']]
                if 'density' in c:
                        e = [float(c['latitude']), float(c['longitude']), float(c['density']), c['post'], c['city'], plot[plot.location_id == c['location']]['sample'].max(), c['location']]
                        a_map.append(e)
        return [a_map, b]

    map_data = map_coords(plot_density[2], slr_beaches)
    map_points = map_data[0]

    def top_ten_codes():
        a = df['quantity'].groupby(df['code_id']).sum()
        b = a.sort_values(ascending=False)
        c = b[:10]
        d = list(c.index)
        f = []
        for g in d:
            for h in codes:
                if h.code == g:
                    f.append({'code':g, 'description':h.description, 'total':c[g]})
        return [a, f]
    slr_top_ten = top_ten_codes()[1]


    color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']
    def sources():
        a = top_ten_codes()[0]
        b = a.to_dict()
        c = b.keys()
        d = []
        for g in codes:
            if g.code in c:
                d.append({'code':g.code, 'source':g.source, 'total':b[g.code]})
        h = pd.DataFrame(d)
        i = h['total'].groupby(h['source']).sum()
        l = sum(i)
        j = []
        for n, r in enumerate(i.index):
            f = (i[n]/l)*100
            k = {'source':f, 'name':r, 'color':color[n]}
            j.append(k)
        return j
    sources_as = sources()

    def locs_and_samples():
        a = df0.groupby('location_id')
        b = a.agg({'density':np.mean, 'sample':max})
        b.reset_index(inplace=True)
        c = b.to_dict('records')
        return c

    return render(request, 'dirt/slr.html', {'sources_as':sources_as, 'slr_top_ten':slr_top_ten, 'summary':summary,
    'plot_density':plot_density[0], 'map_points':map_points, 'slr_cities': cities,'box_plot': box_plot,
    'box_cats':box_cats, 'bx_plot':bx_plot, 'lakes':lakes[0], 'rivers':rivers[0], 'box_lake':box_lake[0], 'box_river':box_river[0], 'locs_samples':locs_and_samples()})


def mcbp_home(request):
    this_data = All_Data.objects.all()
    mcbp_density = All_Data.objects.all().values()
    beaches_v = Beaches.objects.all().values()
    library = References.objects.all()
    beaches = Beaches.objects.all()
    codes = Codes.objects.all()
    sources = Codes.sources()
    mc_beaches = Beaches.beachList()
    #get list and number of locations

    mcbp_total = All_Data.objects.all().aggregate(t_total = Sum('quantity'))

    mc_tot = float(mcbp_total['t_total'])

    t_day = pd.to_datetime('today')

    def make_df(y):
        a = list(y)
        b = pd.DataFrame(a)
        return [a, b]
    dfMC = make_df(this_data)[1]


    def format_data(y):
        a = y.columns
        if 'quantity' in a:
            y = y.astype({'quantity':float}, copy=False)
        if 'density' in a:
            y = y.astype({'density':float}, copy=False)
        if 'date' in a:
            y['date'] = pd.to_datetime(y['date'])
            y = y[y.date < t_day]
        if 'sample' in a:
            y = y.astype({'sample':float}, copy=False)
        if 'length' in a:
            y = y.astype({'length':float}, copy=False)
        return y
    dfMCBP = format_data(make_df(mcbp_density)[1])

    def city_list(city_query):
        b = []
        a = list(city_query)
        for x in a:
            if x['city'] not in b:
                b.append(x['city'])
        return b
    cities = city_list(beaches_v)


    def mcbp_daily():
        a = dfMCBP.copy()
        d =  a['quantity'].groupby([a['date'], a['location_id'], a['length']]).sum()
        e = pd.DataFrame(d)
        e.reset_index(inplace=True)
        e = e[e.date > min(e.date)]
        e['density'] = e['quantity']/e['length']
        e['density'] = e['density'].round(4)
        for name in mc_beaches:
            n=0
            for i, row in e.iterrows():
                if e.loc[i, 'location_id'] == name:
                    n=n+1
                    e.loc[i, 'sample'] = n
        return e
    mc = mcbp_daily()

    def daily_density(df):
        a = df[['date', 'location_id', 'density', 'sample']].copy()
        bb = a[['date', 'location_id', 'density']].copy()
        a['date'] = a['date'].dt.strftime("%Y-%m-%d")
        x = a.to_dict(orient='records')
        b = list(a['density'])
        c = sorted(b)
        d = [x for x in c if x > 0]
        e = [math.log(x) for x in d]

        return [x, e, bb, a, c]
    plot_mc = daily_density(mc)

    def make_summary():
        f = mc.describe()['density']
        num_samps = f['count']
        stan_dev = f['std'].round(2)
        dens_min = f['min'].round(4)
        dens_max = f['max'].round(2)
        two_five = f['25%'].round(2)
        seven_five = f['75%'].round(2)
        average = f['mean'].round(2)
        first_sample = min(mc['date'])
        last_sample = max(mc['date'])
        total = dfMCBP['quantity'].sum()
        iqr = seven_five - two_five
        x = {'first':first_sample, 'last':last_sample, 'num_samps':num_samps, 'ave_dense':average, 'min_dense':dens_min,
        'max_dense':dens_max, 'two_five':two_five, 'seven_five':seven_five, 'stan_dev':stan_dev, 'total':total, 'iqr':iqr}
        return x
    summary = make_summary()

    def map_coords(plot, names ):
        a_map = []
        a = plot['density'].groupby(plot['location_id']).mean().round(6)
        a = a.astype(float)
        b = list(names)
        for c in b:
            if c['location'] in a.index:
                c['density'] = a[c['location']]
                if 'density' in c:
                        e = [float(c['latitude']), float(c['longitude']), float(c['density']), c['post'], c['city'], plot[plot.location_id == c['location']]['sample'].max(), c['location']]
                        a_map.append(e)
        return [a_map, b]

    map_data = map_coords(plot_mc[3], beaches_v)
    map_points = map_data[0]


    def top_ten_codes():
        a = dfMCBP['quantity'].groupby(dfMCBP['code_id']).sum()
        b = a.sort_values(ascending=False)
        c = b[:10]
        d = list(c.index)
        f = []
        for g in d:
            for h in codes:
                if h.code == g:
                    f.append({'code':g, 'description':h.description, 'total':c[g]})
        return [a, f]
    mc_top_ten = top_ten_codes()[1]

    color = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(255, 191, 0, 1)']

    def sources():
        a = top_ten_codes()[0]
        b = a.to_dict()
        c = b.keys()
        d = []
        for g in codes:
            if g.code in c:
                d.append({'code':g.code, 'source':g.source, 'total':b[g.code]})
        h = pd.DataFrame(d)
        i = h['total'].groupby(h['source']).sum()
        l = sum(i)
        j = []
        for n, r in enumerate(i.index):
            f = (i[n]/l)*100
            k = {'source':f, 'name':r, 'color':color[n]}
            j.append(k)
        return j
    sources_as = sources()

    def locs_and_samples():
        a = mc.groupby('location_id')
        b = a.agg({'density':np.mean, 'sample':max})
        b.reset_index(inplace=True)
        c = b.to_dict('records')
        return c

    def box_plots(a):
        a.set_index('date', inplace=True)
        b = a.copy()
        c = b.groupby([b.index.year, b.index.month])
        d = list(c)
        f = []
        for g,h in enumerate(d):
            f.append(d[g][1])
        return f
    mc_box = box_plots(plot_mc[2])

    box_cats = ['Nov-2015', 'Dec-2015', 'Jan-2016', 'Feb-2016', 'Mar-2016', 'Apr-2016', 'May-2016',
    'Jun-2016', 'Jul-2016', 'Aug-2016', 'Sep-2016', 'Oct-2016', 'Nov-2016', 'Dec-2016', 'Jan-2017',
    'Feb-2017', 'Mar-2017','Apr- 2017', 'May- 2017', 'Jun- 2017', 'Jul- 2017', 'Aug- 2017',
    'Sep- 2017', 'Oct- 2017', 'Nov- 2017', 'Dec- 2017', 'Jan- 2018', 'Feb- 2018']


    def boxes(a):
        f = []
        months = box_cats
        for b, c in enumerate(a):
            d = a[b]
            d['density'] = d['density'].astype(float)
            e = list(d['density'])
            g = sorted(e)
            h = [min(g), np.percentile(g, 25, interpolation='lower'), np.median(g), np.percentile(g, 75, interpolation='lower'), max(g)]
            f.append(h)
        return [f, months]

    box_mc = boxes(mc_box)

    def ordered_densities(the_densities):
        t = the_densities
        r = sum(t)/len(t)
        stds = np.std(t)
        h = []
        for m in t:
            g = {'x':float(m), 'y':norm.pdf(float(m), float(r), float(stds))}
            h.append(g)
        return h
    pdf_den = ordered_densities(plot_mc[4])

    def these_logs(the_densities):
        the_logs = [math.log(x) for x in the_densities]
        avg = sum(the_logs)/len(the_logs)
        stds = np.std(the_logs)
        return [the_logs, avg, stds]
    log_it = these_logs(plot_mc[4])

    the_logs = log_it[0]
    avg = log_it[1]
    stds = log_it[2]

    def this_norm(the_logs):
        norms = []
        for this_un in the_logs:
            t = norm.pdf(this_un, avg, stds)
            ugh = [this_un, t]
            norms.append(ugh)
        the_norm = sorted(norms, key=lambda x: x[0])
        return the_norm
    the_norm = this_norm(the_logs)

    def subjects():
        sub_list = library.values_list('subject', flat=True).distinct()
        sub_key = dict(SUBJECT_CHOICES)
        return [sub_list, sub_key]
    the_subs = subjects()[0]
    sub_key = subjects()[1]

    return render(request, 'dirt/mcbp.html', {'summary':summary, 'cities':cities, 'map_points':map_points, 'plot_mc':plot_mc[0],
    'boxer':box_mc[0],'box_cats':box_cats, 'pdf_den':pdf_den, 'the_norm':the_norm, 'locs_samples': locs_and_samples(),
    'mc_top_ten':mc_top_ten, 'sources_as':sources_as, 'subjects':subjects, 'sub_key':sub_key, 'library':library })
