# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum, Avg, Max, Min
from django.contrib.auth.models import UserManager


WATER_CHOICES = (
    ('r', 'river'),
    ('l', 'lake')
    )

class Beaches(models.Model):
    """
    Beach names and gps data, Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='location', max_length=100, blank=True, null=False, primary_key=True)  # Field name made lowercase.
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=100, blank=True, null=True)
    post = models.CharField(db_column='post', max_length=12, blank=True, null=True)
    water = models.CharField(db_column='water', max_length=12, blank=True, null=True, choices=WATER_CHOICES)

    def beachList():
        nameList = []
        for x in Beaches.objects.values('location'):
            for t, y in x.items():
                nameList.append(y)
        return nameList


    def __str__(self):
        return u'location:%s, lat:%s, lon:%s, city:%s, water:%s, post:%s'%(self.location, self.latitude, self.longitude, self.city, self.water, self.post)

    class Meta:
        managed = False
        db_table = 'beaches'
        ordering = ['location']

class SLR_Beaches(models.Model):
    """
    Beach names and gps data, Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=False, primary_key=True)  # Field name made lowercase.
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=100, blank=True, null=True)
    post = models.CharField(db_column='post', max_length=12, blank=True, null=True)
    water = models.CharField(db_column='water', max_length=12, blank=True, null=True, choices=WATER_CHOICES)

    def beachList():
        nameList = []
        for x in SLR_Beaches.objects.values('location'):
            for t, y in x.items():
                nameList.append(y)
        return nameList


    def __str__(self):
        return u'location:%s, lat:%s, lon:%s'%(self.location, self.latitude, self.longitude)

    class Meta:
        managed = False
        db_table = 'slr_beaches'
        ordering = ['location']


class Codes(models.Model):
    """
    MLW codes and decriptions, Codes.materials() gives a list of the materials,
    Codes.describe() gives a list of the items characeterized by the MLW code,
    Codes.sources() gives a list of the sources as defined for this study.
    """
    code = models.CharField(db_column='code', max_length=5, blank=True, null=False, primary_key=True)
    material = models.CharField(db_column='material', max_length=30, blank=True, null=True)
    description = models.CharField(db_column='description', max_length=30, blank=True, null=True)
    source = models.CharField(db_column='source', max_length=30, blank=True, null=True)

    def materials():
        matList = []
        for x in Codes.objects.values('material'):
            for t, y in x.items():
                if y not in matList:
                    matList.append(y)
        return matList
    def describe():
        descriptions = []
        for x in Codes.objects.values('description'):
            for t, y in x.items():
                if y not in descriptions:
                    descriptions.append(y)
        return descriptions
    def sources():
        sourceList = []
        for x in Codes.objects.values('source'):
            for t, y in x.items():
                if y not in sourceList:
                    sourceList.append(y)
        return sourceList
    def codes():
        return Codes.objects.values('code')

    objects = UserManager()


    def __str__(self):
        return u'code:%s, material:%s, source:%s, description:%s' %(self.code, self.material, self.source, self.description)


    class Meta:
        managed = False
        db_table = 'codes'
        ordering = ['material']

class All_Data(models.Model):
    location = models.ForeignKey(Beaches, db_column='location', on_delete=models.DO_NOTHING)  # Field name made lowercase.
    date = models.DateField(db_column='date', blank=True, null=True)  # Field name made lowercase.
    length = models.DecimalField(db_column='length', decimal_places=2, max_digits= 7, blank=True, null=True)
    quantity = models.DecimalField(db_column='quantity',decimal_places=2, max_digits= 7, blank=True, null=True)
    # key = models.IntegerField(db_column='id',blank=True, null=False, primary_key=True)
    code = models.ForeignKey(Codes, db_column='code', on_delete=models.DO_NOTHING)


    class Meta:
        managed = False
        db_table = 'all_items'
    def __str__(self):
        return u"date:%s, source:%s, location:%s, length:%s, quantity:%s, code:%s" %(self.date, self.code.source, self.location, self.length, self.quantity, self.code, )

class SLR_Data(models.Model):
    location = models.ForeignKey(SLR_Beaches, db_column='location', on_delete=models.DO_NOTHING)  # Field name made lowercase.
    date = models.DateField(db_column='date', blank=True, null=True)  # Field name made lowercase.
    length = models.DecimalField(db_column='length', decimal_places=2, max_digits= 7, blank=True, null=True)
    quantity = models.DecimalField(db_column='quantity',decimal_places=2, max_digits= 7, blank=True, null=True)
    density = models.DecimalField(db_column='density', decimal_places=3, max_digits=8, blank=True, null=False,)
    code = models.ForeignKey(Codes, db_column='code', on_delete=models.DO_NOTHING)


    class Meta:
        managed = False
        db_table = 'slr_data'
    def __str__(self):
        return u"date:%s,location:%s, length:%s, code:%s, quantity:%s, density:%s" %(self.date, self.location, self.length, self.code, self.quantity, self.density,)

class SLR_Density(models.Model):
    location = models.ForeignKey(SLR_Beaches, db_column='location', on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=True, null=True)
    sample = models.IntegerField(db_column='sample', blank=True, null=True)
    density = models.DecimalField(db_column='density', decimal_places=3, max_digits=8, blank=True, null=False)
    quantity = models.IntegerField(db_column='quantity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'slr_dens_date'
    def __str__(self):
        return u"date:%s, location:%s, density:%s, sample:%s, quantity:%s" %(self.date, self.location, self.density, self.sample, self.quantity)


class Try_this(All_Data):
    class Meta:
        proxy = True
    def all_beaches():
        b = All_Data.objects.all()
        c = b.aggregate(Sum('quantity'))
        # for d in b:
        #     c['this_total'].append(d['quantity'])
        # d = sum(c['this_total'])
        return [c,b]


    def this_beach(a):
        b = Beaches.beachList()
        c = []
        for d in b:
            c.append(a.filter(location=c))
        return c

    colors = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(22, 199, 158, 1)']

    # def source_dict():
    #     a = {}
    #     sources = Codes.sources()
    #     sources.remove('None')
    #     for b in sources:
    #         a.update({b:[]})
    #     return a
    # def code_dict():
    #
    # def source_values():
    #     a = Try_this.source_dict()
    #     b = a.keys()
    #     this_data = Try_this.all_beaches()[1]
    #     for c in this_data:
    #         if c.code.source in b:
    #             a[c.code.source].append(c.quantity)
    #     return a

    # def source_totals():
    #     colors = ['rgb(10, 46, 92, 1)', 'rgb(71, 142, 235, 1)', 'rgb(163, 199, 245, 1)', 'rgb(115, 18, 13, 1)', 'rgb(199, 31, 22, 1)', 'rgb(13, 115, 91, 1)', 'rgb(22, 199, 158, 1)', 'rgb(121, 70, 40, 1)', 'rgb(159, 183, 159, 1)', 'rgb(102,102, 0, 1)', 'rgb(215, 78, 9, 1)', 'rgb(22, 199, 158, 1)']
    #     a = Try_this.source_values()
    #     a.pop('None')
    #     b = {}
    #     c = Try_this.all_beaches()[0]
    #     e = c['quantity__sum']
    #     for r,d in a.items():
    #         f = sum(d)
    #         g = f/e*100
    #         b.update({r:g})
    #     l = {}
    #     for i, j in zip(b.items(), colors):
    #         k = {'name':i[0], 'data':i[1], 'color':j}
    #         l.update(k)
    #
    #     return l

    # def this_source():
    #     a = Try_this.all_beaches()[1]
    #     b = Codes.sources()
    #     c = {}
    #     for d in b:
    #         c.update({d:})

    def __str__(self):
        return d

    # def __str__(self):
    #     return u"date:%s, location:%s, length:%s, quantity:%s, code:%s" %(self.date, self.location, self.length, self.quantity, self.code)



FINANCE_CHOICES = (
    ('t', 'Transportation'),
    ('m', 'Meals'),
    ('s', 'Software'),
    ('n', 'Network'),
    ('t', 'Telephone'),
    ('p', 'Personal equipment'),
    ('e', 'Equipment'),
    ('i', 'IT equipment'),
    ('o', 'Operations'),
    ('d', 'Donation'),
    ('s-g', 'Services group activity'),
    ('s-c', 'Services beach clean'),
    ('s-s', 'Services IT'),
    ('l', 'labor' ),
)

ENTRY_CHOICES = (
    ('ex', 'expense'),
    ('re', 'revenue')
)

class Finance(models.Model):
    date = models.DateField(db_column='date', blank=True, null=True)
    entry = models.CharField(db_column='type', max_length=30, choices=ENTRY_CHOICES)
    origin = models.CharField(db_column='source', max_length=30, choices=FINANCE_CHOICES)
    amount = models.DecimalField(db_column='amount', decimal_places=2, max_digits=10, blank=True, null=True)
    project = models.CharField(db_column='project', max_length=30, blank=True)

    class Meta:
        managed = False
        db_table = 'finance'
    def __str__(self):
        return u"date:%s, entry:%s, origin:%s, amount:%s, project:%s" %(self.date, self.entry, self.origin, self.amount, self.project)


SUBJECT_CHOICES = (
    ('env', 'Environment - general'),
    ('env-h', 'Hydrology'),
    ('env-j', 'Environment - justice'),
    ('wat-q', 'Water quality'),
    ('bio', 'Biology - general'),
    ('chem', 'Chemistry'),
    ('m-bio', 'Microbiology'),
    ('b-l', 'Beach-litter'),
    ('econ', 'Economics'),
    ('cit', 'Citizen science'),
    ('gv', 'Government - reg'),
    ('mt', 'Math - general'),
    ('ma', 'Math - Analysis'),
    ('mp', 'Math - probability'),
    ('pp', 'Programing - python'),
    ('pd', 'Data science'),
    ('po', 'Programing - other'),
    ('gc', 'General culture'),

)

class References(models.Model):
    title = models.CharField(db_column='title', max_length=240, blank=True, null=True)
    author = models.CharField(db_column='author', max_length=120, blank=True, null=True)
    abstract = models.CharField(db_column='abstract', max_length=300, blank=True, null=True)
    subject = models.CharField(db_column='subject', max_length=30, choices=SUBJECT_CHOICES)

    def __str__(self):
        return u"title:%s, author:%s, abstract:%s, subject:%s" %(self.title, self.author, self.abstract, self.subject)

    class Meta:
        managed = False
        db_table = 'library'

class Densities(models.Model):
    location = models.CharField(db_column='Location', max_length=30, blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    total = models.IntegerField(db_column='total', blank=True, null=True)
    length = models.IntegerField(db_column='length', blank=True, null=True)
    density = models.DecimalField(db_column='density', max_digits=5, decimal_places=2, blank=True, null=True)
    # key = models.IntegerField(db_column='id',blank=True, null=False, primary_key=True)

    def __str__(self):
        return u"%s, date:%s; %s, 'length':%s" %(self.location, self.date, self.density, self.length)

    class Meta:
        managed = True
        db_table = 'densities'
        ordering = ['date']

class Totals(models.Model):
    code = models.CharField(db_column='mlw', max_length=30, blank=False, null=False, primary_key=True)
    Arabie = models.IntegerField(db_column='Arabie', blank=True, null=True)
    Bain_des_Dames = models.IntegerField(db_column='Bain_des_Dames', blank=True, null=True)
    Baye_de_Clarens = models.IntegerField(db_column='Baye_de_Clarens', blank=True, null=True)
    Baye_de_Montreux_D = models.IntegerField(db_column='Baye_de_Montreux_D', blank=True, null=True)
    Baye_de_Montreux_G = models.IntegerField(db_column='Baye_de_Montreux_G', blank=True, null=True)
    Boiron = models.IntegerField(db_column='Boiron', blank=True, null=True)
    Grand_Clos = models.IntegerField(db_column='Grand_Clos', blank=True, null=True)
    Jardin_Botanique = models.IntegerField(db_column='Jardin_Botanique', blank=True, null=True)
    La_Morges = models.IntegerField(db_column='La_Morges', blank=True, null=True)
    Le_Pierrier = models.IntegerField(db_column='Le_Pierier', blank=True, null=True)
    Le_Port = models.IntegerField(db_column='Le_Port', blank=True, null=True)
    Maladaire = models.IntegerField(db_column='Maladaire', blank=True, null=True)
    Oyonne = models.IntegerField(db_column='Oyonne', blank=True, null=True)
    Parc_des_Pierrettes = models.IntegerField(db_column='Parc_des_Pierrettes', blank=True, null=True)
    Pierrier_sud = models.IntegerField(db_column='Pierier_sud', blank=True, null=True)
    Plage_de_Dorigny = models.IntegerField(db_column='Plage_de_Dorigny', blank=True, null=True)
    Plage_de_St_Sulpice = models.IntegerField(db_column='Plage_de_St_Sulpice', blank=True, null=True)
    Quai_Maria_Belgia = models.IntegerField(db_column='Quai_Maria_Belgia', blank=True, null=True)
    Thonnon_les_Bains = models.IntegerField(db_column='Thonnon_les_Bains', blank=True, null=True)
    Versoix = models.IntegerField(db_column='Versoix', blank=True, null=True)
    Veveyse = models.IntegerField(db_column='Veveyse', blank=True, null=True)
    Vidy = models.IntegerField(db_column='Vidy', blank=True, null=True)
    Villa_Barton = models.IntegerField(db_column='Villa_Barton', blank=True, null=True)
    # key = models.IntegerField(db_column='id',blank=True, null=False, primary_key=True)


    def __str__(self):
        return u'code:%s, Arabie:%s, Bain des Dames:%s, Baye de Clarens:%s, Baye de Montreux - D:%s, Baye de Montreux - G:%s, Boiron:%s, Grand Clos:%s, Jardin Botanique:%s, La Morges:%s, Le Pierrier:%s, Le Port:%s, Maladaire:%s, Oyonne:%s, Parc des Pierrettes:%s, Pierrier sud:%s, Plage de Dorigny:%s, Plage de St Sulpice:%s, Quai Maria Belgia:%s, Thonnon les Bains:%s, Versoix:%s, Veveyse:%s, Vidy:%s, Villa Barton:%s' %(self.code, self.Arabie, self.Bain_des_Dames, self.Baye_de_Clarens, self.Baye_de_Montreux_D, self.Baye_de_Montreux_G, self.Boiron, self.Grand_Clos, self.Jardin_Botanique, self.La_Morges, self.Le_Pierrier, self.Le_Port, self.Maladaire, self.Oyonne, self.Parc_des_Pierrettes, self.Pierrier_sud, self.Plage_de_Dorigny, self.Plage_de_St_Sulpice, self.Quai_Maria_Belgia, self.Thonnon_les_Bains, self.Versoix, self.Veveyse, self.Vidy, self.Villa_Barton)

    class Meta:
        managed = True
        db_table = 'codes_totals'





class Material(models.Model):
    location = models.CharField(db_column='Location', max_length=30, blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    chemicals = models.IntegerField(db_column='Chemicals', blank=True, null=True)  # Field name made lowercase.
    cloth = models.IntegerField(db_column='Cloth', blank=True, null=True)  # Field name made lowercase.
    glass = models.IntegerField(db_column='Glass', blank=True, null=True)  # Field name made lowercase.
    metal = models.IntegerField(db_column='Metal', blank=True, null=True)  # Field name made lowercase.
    paper = models.IntegerField(db_column='Paper', blank=True, null=True)  # Field name made lowercase.
    plastic = models.IntegerField(db_column='Plastic', blank=True, null=True)  # Field name made lowercase.
    rubber = models.IntegerField(db_column='Rubber', blank=True, null=True)  # Field name made lowercase.
    unidentified = models.IntegerField(db_column='Unidentified', blank=True, null=True)  # Field name made lowercase.
    wood = models.IntegerField(db_column='Wood', blank=True, null=True)  # Field name made lowercase.
    Total = models.IntegerField(db_column='Total', blank=True, null=True)  # Field name made lowercase.
    # key = models.IntegerField(db_column='id',blank=True, null=False, primary_key=True)

    def __str__(self):
        return u'location:%s, date:%s, chemicals:%s, cloth:%s, glass:%s, metal:%s, paper:%s, plastic:%s, rubber:%s, unidentified:%s, wood:%s, total:%s,' %(self.location, self.date, self.chemicals, self.cloth, self.glass, self.metal, self.paper, self.plastic, self.rubber, self.unidentified, self.wood, self.Total)


    class Meta:
        managed = True
        db_table = 'material'
        ordering = ['date']


class Source(models.Model):
    location = models.CharField(db_column='Location', max_length=30, blank=True, null=True, )  # Field name made lowercase.
    Date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    Construction = models.IntegerField(db_column='Construction', blank=True, null=True)  # Field name made lowercase.
    Fishing = models.IntegerField(db_column='Fishing', blank=True, null=True)  # Field name made lowercase.
    Food = models.IntegerField(db_column='Food', blank=True, null=True)  # Field name made lowercase.
    Fragment = models.IntegerField(db_column='Fragment', blank=True, null=True)  # Field name made lowercase.
    Household = models.IntegerField(db_column='Household', blank=True, null=True)  # Field name made lowercase.
    Industry = models.IntegerField(db_column='Industry', blank=True, null=True)  # Field name made lowercase.
    Medical = models.IntegerField(db_column='Medical', blank=True, null=True)  # Field name made lowercase.
    Other = models.IntegerField(db_column='Other', blank=True, null=True)  # Field name made lowercase.
    Personal = models.IntegerField(db_column='Personal', blank=True, null=True)  # Field name made lowercase.
    Recreation = models.IntegerField(db_column='Recreation', blank=True, null=True,)# Field name made lowercase.
    Tobaco = models.IntegerField(db_column='Tobaco', blank=True, null=True)  # Field name made lowercase.
    Water_treatment = models.IntegerField(db_column='Water_treament', blank=True, null=True, )  # Field name made lowercase.
    Total = models.IntegerField(db_column='Total', blank=True, null=True)  # Field name made lowercase.
    # Key = models.IntegerField(db_column='id',blank=True, null=False, primary_key=True)

    def __str__(self):
        return u"Location:%s, Date:%s, Construction:%s, Fishing:%s, Food:%s, Fragment:%s, Household:%s, Industry:%s, Medical:%s, Other:%s, Personal:%s, Recreation:%s, Tobaco:%s, Water_treatment:%s, Total:%s)"  %(self.location, self.Date, self.Construction, self.Fishing, self.Food, self.Fragment, self.Household, self.Industry, self.Medical, self.Other, self.Personal, self.Recreation, self.Tobaco, self.Water_treatment, self.Total)

    objects = UserManager()

    class Meta:
        managed = True
        db_table = 'source'
        ordering = ['Date']
