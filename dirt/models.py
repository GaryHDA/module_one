from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum, Avg, Max, Min, F
from django.contrib.auth.models import UserManager, User
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime

WATER_CHOICES = (
    ('r', 'river'),
    ('l', 'lake')
    )
class Projects(models.Model):
    """
    Projects using the platform
    """
    project = models.CharField(db_column='project', max_length=100, blank=False, null=False, primary_key=True, default='Your project')
    org = models.CharField(db_column='org', max_length=100, blank=True, null=True, default='Your-org' )
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel')

    def projectList():
        d = []
        for a in Projects.objects.values('project'):
            for b, c in a.items():
                d.append(c)
        return d

    def __str__(self):
        return u'project:%s, org:%s'%(self.project, self.org)

    class Meta:
        managed = True
        db_table = 'projects'
        ordering = ['project']
        verbose_name_plural = 'Projects'
class Beaches(models.Model):
    """
    Beach names and gps data, Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='location', max_length=100, primary_key=True, blank=False, null=False,  default='location required')
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=False, null=False,  default=111.11111)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=False, null=False,  default=11.11111)
    city = models.CharField(db_column='city', max_length=100, blank=False, null=False,  default='City required')
    post = models.CharField(db_column='post', max_length=12, blank=False, null=False,  default='Postal-code')
    water = models.CharField(db_column='water', max_length=12, blank=False, null=False, choices=WATER_CHOICES, default='l')
    water_name = models.CharField(db_column='water_name', max_length=100, blank=False, null=False,  default='Lake or river name required')
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40, blank=True, null=False, default='mwshovel',)

    def __str__(self):
        return u'location:%s, lat:%s, lon:%s, city:%s, water:%s, post:%s, project:%s, owner:%s'%(self.location, self.latitude, self.longitude, self.city, self.water, self.post, self.project, self.owner)

    class Meta:
        managed = True
        db_table = 'beaches'
        ordering = ['location']
        verbose_name_plural = 'Beaches-Europe'
class HDC_Beaches(models.Model):
    """
    Beach names for hd california and gps data, Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='location', max_length=100, primary_key=True, blank=False, null=False,  default='location required')
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=False, null=False,  default=111.11111)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=False, null=False,  default=11.11111)
    city = models.CharField(db_column='city', max_length=100, blank=False, null=False,  default='City required')
    post = models.CharField(db_column='post', max_length=12, blank=False, null=False,  default='Postal-code')
    water = models.CharField(db_column='water', max_length=12, blank=False, null=False, choices=WATER_CHOICES, default='r')
    water_name = models.CharField(db_column='water_name', max_length=100, blank=False, null=False,  default='Lake or river name required')
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False, default='mwshovel',)

    def __str__(self):
        return u'location:%s, lat:%s, lon:%s, city:%s, water:%s, post:%s, project:%s'%(self.location, self.latitude, self.longitude, self.city, self.water, self.post, self.project)

    class Meta:
        managed = True
        db_table = 'hdrc_beaches'
        ordering = ['location']
        verbose_name_plural = 'Beaches-California'

class Codes(models.Model):
    """
    MLW codes and decriptions, Codes.materials() gives a list of the materials,
    Codes.describe() gives a list of the items characeterized by the MLW code,
    Codes.sources() gives a list of the sources as defined for this study.
    """
    code = models.CharField(db_column='code', max_length=5, primary_key=True, blank=False, null=False, default='Code')
    material = models.CharField(db_column='material', max_length=30, blank=False, null=False, default='An MLW material type')
    description = models.CharField(db_column='description', max_length=30, blank=False, null=False, default='Describe the item')
    source = models.CharField(db_column='source', max_length=30, blank=False, null=False, default='Where does it come from')
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)

    objects = UserManager()

    def __str__(self):
        return u'code:%s, material:%s, source:%s, description:%s' %(self.code, self.material, self.source, self.description)

    class Meta:
        managed = True
        db_table = 'codes'
        ordering = ['material']
        verbose_name_plural = 'MLW codes'

class AllData(models.Model):
    location = models.ForeignKey(Beaches, db_column='location',null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today )
    length = models.IntegerField(db_column='length', blank=False, null=False, default=1)
    quantity = models.IntegerField(db_column='quantity', blank=False, null=False, default=1)
    code = models.ForeignKey(Codes, db_column='code', null=True,  on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40, blank=False, null=False,default='mwshovel',)

    class Meta:
        get_latest_by = 'date'
        managed = True
        db_table = 'all_items'
        verbose_name_plural = 'All data Europe'
    def __str__(self):
        return u"date:%s, source:%s, location:%s, length:%s, quantity:%s, code:%s, " %(self.date, self.code.source, self.location.location, self.length, self.quantity, self.code  )

class HDC_Data(models.Model):
    location = models.ForeignKey(HDC_Beaches, db_column='location', null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today )
    length = models.IntegerField(db_column='length', blank=False, null=False, default=1)
    quantity = models.IntegerField(db_column='quantity', blank=False, null=False, default=1)
    code = models.ForeignKey(Codes, db_column='code', null=True,  on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40, blank=False, null=False,default='mwshovel',)

    class Meta:
        get_latest_by = 'date'
        managed = True
        db_table = 'hdrc_copy'
        verbose_name_plural = 'All data California'
    def __str__(self):
        return u"date:%s, source:%s, location:%s, length:%s, quantity:%s, code:%s, " %(self.date, self.code.source, self.location.location, self.length, self.quantity, self.code  )


FINANCE_CHOICES = (
    ('t-r', 'Transportation'),
    ('m', 'Meals'),
    ('s', 'Software'),
    ('n', 'Network'),
    ('t', 'Telephone'),
    ('p', 'Personal equipment'),
    ('e', 'Equipment'),
    ('i', 'IT equipment'),
    ('o', 'Operations'),
    ('d', 'Donation'),
    ('sp', 'sponsor'),
    ('s-g', 'Services group activity'),
    ('s-c', 'Services beach clean'),
    ('s-s', 'Services IT'),
    ('l', 'labor'),
    ('c', 'consultation-meeting' ),
)

ENTRY_CHOICES = (
    ('ex', 'expense'),
    ('re', 'revenue')
)

PAID = (
('y', 'YES'),
('n', 'NO'),
)

class Finance(models.Model):
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today)
    entry = models.CharField(db_column='type', max_length=30, blank=False, null=False, choices=ENTRY_CHOICES)
    origin = models.CharField(db_column='source', max_length=30, blank=False, null=False, choices=FINANCE_CHOICES)
    amount = models.DecimalField(db_column='amount', decimal_places=2, max_digits=10, blank=False, null=False, default=1.0)
    is_paid = models.CharField(db_column='is_paid', max_length=30, default='n', choices=PAID)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    client = models.CharField(db_column='client', max_length=40, blank=False, null=False, default='Who')
    comments = models.CharField(db_column='comments', max_length=100, blank=False, null=False, default='Comment is required like "Why?"')
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)

    class Meta:
        managed = True
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
    ('pjs', 'Programing - JavaScript'),
    ('pd', 'Data science'),
    ('po', 'Programing - other'),
    ('gc', 'General culture'),
    ('qe', 'Quant econ'),


)

class References(models.Model):
    title = models.CharField(db_column='title', max_length=240, blank=False, null=False, default='Titles are required')
    author = models.CharField(db_column='author', max_length=120, blank=False, null=False, default='Authors deserve credit')
    abstract = models.CharField(db_column='abstract', max_length=300,  blank=False, null=False, default='What is this about')
    subject = models.CharField(db_column='subject', max_length=30, choices=SUBJECT_CHOICES)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today)
    def __str__(self):
        return u"title:%s, author:%s, abstract:%s, subject:%s" %(self.title, self.author, self.abstract, self.subject)

    class Meta:
        managed = True
        get_latest_by = 'date'
        db_table = 'library'
        verbose_name_plural = 'References'

PLATFORM_CHOICES = (
    ('SO', 'Stack Overflow'),
    ('SE-M', 'StackExchange Math'),
    ('M', 'Medium'),
    )

class PlatformActivity(models.Model):
    platform = models.CharField(db_column='platform', max_length=30, choices=PLATFORM_CHOICES)
    subject = models.CharField(db_column='subject', max_length=30, choices=SUBJECT_CHOICES)
    comments = models.CharField(db_column='comments', max_length=240, blank=False, null=False, default='What is this about')
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today)
    ur_l = models.URLField(db_column='url', blank=True, null=True)
    owner = models.CharField(db_column='owner', max_length=40, blank=False, null=False,default='mwshovel',)

    def __str__(self):
        return u"platform:%s, subject:%s, comments:%s, date:%s, ur_l:%s, owner:%s" %(self.platform, self.subject, self.comments, self.date, self.ur_l, self.owner)

    class Meta:
        managed = True
        get_latest_by = 'date'
        db_table = 'platform_activity'
        verbose_name_plural = 'Recent posts'

class LastCommit(models.Model):
    repo = models.CharField(db_column='repo', max_length=240, blank=False, null=False, default='Name of the repository')
    comments = models.CharField(db_column='comments', max_length=240, blank=False, null=False, default='What is this about')
    date = models.DateField(db_column='date', blank=False, null=False, default=datetime.date.today)
    ur_l = models.URLField(db_column='url', blank=True, null=True)
    owner = models.CharField(db_column='owner', max_length=40, blank=False, null=False,default='mwshovel',)

    def __str__(self):
        return u"repo:%s, comments:%s, date:%s, ur_l:%s, owner:%s" %(self.repo, self.comments, self.date, self.ur_l, self.owner)

    class Meta:
        managed = True
        get_latest_by = 'date'
        db_table = 'last_commit'
        verbose_name_plural = 'Recent posts'


CONTRACT_CHOICES = (
    ('l', 'location'),
    ('l-m', 'location-multiple'),
    ('m-l', 'mulitple-locations'),
    ('l-2', 'location-half'),
    ('l-3', 'location-third'),
)
STAFF = (
('m', 'member'),
('v', 'volunteer'),
('s', 'sponsor')
)


class Sponsors(models.Model):
    sponsor = models.CharField(db_column='sponsor', max_length=120, blank=False, null=False, primary_key=True)
    is_staff = models.CharField(db_column='is_staff', max_length=14, choices=STAFF)
    sponsor_url = models.URLField(db_column='url', blank=True, null=True)
    sponsor_icon_name = models.CharField(db_column='icon', max_length=120, blank=False, null=False, default='images/icon_one.jpeg')
    message = models.CharField(db_column='message', max_length=380, blank=False, null=False, default='Why do you do it?')
    beach = models.ManyToManyField(Beaches)
    ca_beach = models.ManyToManyField(HDC_Beaches)

    def __str__(self):
        return u"sponsor:%s, beach:%s" %(self.sponsor, self.beach)

    class Meta:
        managed = True
        db_table = 'sponsors'
        verbose_name_plural = 'Sponsors'
    def __str__(self):
        return u"sponsor:%s, url:%s, icon:%s, message:%s" %(self.sponsor, self.sponsor_url, self.sponsor_icon_name, self.message,)

# The modles below are not managed by the ORM, this data is static. The data tables exist.
# the contentst of SLR_Data and SLR_Beaches has been folded into AllData and Beaches.
class SLR_Beaches(models.Model):
    """
    Beach names and gps data, SLR_Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=False, primary_key=True)
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=100, blank=True, null=True)
    post = models.CharField(db_column='post', max_length=12, blank=True, null=True)
    water = models.CharField(db_column='water', max_length=12, blank=True, null=True, choices=WATER_CHOICES)
    water_name = models.CharField(db_column='water_name', max_length=100, blank=True, null=True)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)


    def __str__(self):
        return u'location:%s, lat:%s, lon:%s, city:%s, water:%s, post:%s, project:%s'%(self.location, self.latitude, self.longitude, self.city, self.water, self.post, self.project)

    class Meta:
        managed = False
        db_table = 'slr_beaches'
        ordering = ['location']



class SLR_Data(models.Model):
    location = models.ForeignKey(SLR_Beaches, db_column='location', null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=True, null=True)
    length = models.IntegerField(db_column='length', default=0)
    quantity = models.IntegerField(db_column='quantity', default=0)
    density = models.DecimalField(db_column='density', decimal_places=3, max_digits=8, blank=True, null=False,)
    code = models.ForeignKey(Codes, db_column='code', null=True, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)

    class Meta:
        managed = False
        db_table = 'slr_data'
    def __str__(self):
        return u"date:%s,location:%s, length:%s, code:%s, quantity:%s, density:%s" %(self.date, self.location, self.length, self.code, self.quantity, self.density,)

    def location_name(self):
        return self.location.location
class SLR_Density(models.Model):
    location = models.ForeignKey(SLR_Beaches, db_column='location', null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=True, null=True)
    sample = models.IntegerField(db_column='sample', blank=True, null=True)
    density = models.DecimalField(db_column='density', decimal_places=3, max_digits=8, blank=True, null=False)
    quantity = models.IntegerField(db_column='quantity', blank=True, null=True)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'slr_dens_date'
    def __str__(self):
        return u"date:%s, location:%s, density:%s, sample:%s, quantity:%s" %(self.date, self.location, self.density, self.sample, self.quantity)
class SLR_Area(models.Model):
    location = models.ForeignKey(SLR_Beaches, db_column='location', null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=True, null=True)
    sample = models.IntegerField(db_column='sample', blank=True, null=True)
    density2 = models.DecimalField(db_column='density2', decimal_places=3, max_digits=8, blank=True, null=False)
    quantity = models.IntegerField(db_column='quantity', default=0)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.CharField(db_column='owner', max_length=40,blank=True, null=False,default='mwshovel',)

    class Meta:
        managed = False
        db_table = 'slr_area'
    def __str__(self):
        return u"date:%s, location:%s, density:%s, sample:%s, quantity:%s" %(self.date, self.location, self.density, self.sample, self.quantity)
