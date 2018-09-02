from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum, Avg, Max, Min, F
from django.contrib.auth.models import UserManager, User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
WATER_CHOICES = (
    ('r', 'river'),
    ('l', 'lake')
    ('o', 'ocean')
    )
class Project(models.Model):
    """
    Projects using the platform
    """
    project = models.CharField(db_column='project', max_length=100, blank=True, null=False, primary_key=True)
    org = models.CharField(db_column='org', max_length=100, blank=True, null=True, )
    org_email = models.CharField(validators=[validate_email])
    owner = models.ForeignKey(get_user_model(), db_column='owner', related_name='owner', on_delete=models.DO_NOTHING)

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
        db_table = 'project'
        ordering = ['project']

class Beach(models.Model):
    """
    Beach names and gps data, Beaches.beachList() returns a list of just beach names.
    """
    location = models.CharField(db_column='location', max_length=100, blank=True, null=False, primary_key=True)  # Field name made lowercase.
    latitude = models.DecimalField(db_column='latitude', max_digits=11, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(db_column='longitude', max_digits=11, decimal_places=8, blank=True, null=True)
    city = models.CharField(db_column='city', max_length=100, blank=True, null=True)
    post = models.CharField(db_column='post', max_length=12, blank=True, null=True)
    departement = models.IntegerField(db_column='length', default=0)
    water = models.CharField(db_column='water', max_length=12, blank=True, null=True, choices=WATER_CHOICES)
    water_name = models.CharField(db_column='water_name', max_length=100, blank=True, null=True)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(get_user_model(), db_column='owner', on_delete=models.DO_NOTHING)



    def __str__(self):
        return u'location:%s, lat:%s, lon:%s, city:%s, post:%s, departement:%s, water:%s, post:%s, project:%s'%(self.location, self.latitude, self.longitude, self.city, self.post, self.departement, self.water,  self.project)

    class Meta:
        managed = True
        db_table = 'beach'
        ordering = ['location']

class Code(models.Model):
    """
    MLW codes and decriptions, Codes.materials() gives a list of the materials,
    Codes.describe() gives a list of the items characeterized by the MLW code,
    Codes.sources() gives a list of the sources as defined for this study.
    """
    m_code = models.CharField('MLW code', db_column='code', max_length=5, blank=True, null=False, primary_key=True)
    o_code = models.CharField('OSPAR code', db_column='code', max_length=5, blank=True, null=False, primary_key=True)
    material = models.CharField(db_column='material', max_length=30, blank=True, null=True)
    description = models.CharField(db_column='description', max_length=30, blank=True, null=True)
    # source = models.CharField(db_column='source', max_length=30, blank=True, null=True)
    owner = models.ForeignKey(get_user_model(), db_column='owner',  on_delete=models.DO_NOTHING)

    objects = UserManager()


    def __str__(self):
        return u'MLW code:%s, OSPAR code:%s material:%s, source:%s, description:%s' %(self.m_code, self.o_code, self.material, self.source, self.description)


    class Meta:
        managed = True
        db_table = 'code'
        ordering = ['material']


EVENT_CHOICES = (
    ('i', 'inventory'),
    ('w', 'weight'),
    ('v', 'volume'),
    ('w-v', 'weght and volume')
    )


class Event(models.Model):
    location = models.ForeignKey(Beaches, db_column='location', null=True, on_delete=models.DO_NOTHING)
    date = models.DateField(db_column='date', blank=True, null=True)
    length = models.IntegerField(db_column='length', default=0)
    method = models.CharField(db_column='method', max_length=12, blank=True, null=True, choices=EVENT_CHOICES)
    volume = models.IntegerField(db_column='quantity', default=0)
    weight = models.ForeignKey(Codes, db_column='code', null=True,  on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    time = models.IntegerField(db_column='time', default=0 )
    owner = models.ForeignKey(get_user_model(), db_column='owner',  on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'event'
    def __str__(self):
        return u"date:%s, location:%s, length:%s, volume:%s, weight:%s, project:%s " %(self.date, self.location, self.length, self.volume, self.weight, self.project)

    @property
    def location_name(self):
        return self.location.location

class ItemData(models.Model):
    location = models.ForeignKey(Beache, db_column='location', null=True, on_delete=models.DO_NOTHING)  # Field name made lowercase.
    date = models.DateField(db_column='date', blank=True, null=True)  # Field name made lowercase.
    length = models.IntegerField(db_column='length', default=0)
    quantity = models.IntegerField(db_column='quantity', default=0)
    code = models.ForeignKey(Codes, db_column='code', null=True,  on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(get_user_model(), db_column='owner', on_delete=models.DO_NOTHING)


    class Meta:
        managed = True
        db_table = 'itemdata'
    def __str__(self):
        return u"date:%s, source:%s, location:%s, length:%s, quantity:%s, code:%s, " %(self.date, self.code.source, self.location, self.length, self.quantity, self.code  )
    def location_name(self):
        return self.location.location



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

class Finance(models.Model):
    date = models.DateField(db_column='date', blank=True, null=True)
    entry = models.CharField(db_column='type', max_length=30, choices=ENTRY_CHOICES)
    origin = models.CharField(db_column='source', max_length=30, choices=FINANCE_CHOICES)
    amount = models.DecimalField(db_column='amount', decimal_places=2, max_digits=10, blank=True, null=True)
    project = models.CharField(db_column='project', max_length=30, blank=True)
    client = models.CharField(db_column='client', max_length=40, blank=True)
    comments = models.CharField(db_column='comments', max_length=100, blank=True)
    owner = models.ForeignKey(get_user_model(), db_column='owner',  on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'merterfinance'
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
    project = models.ForeignKey(Projects, db_column='project',null=True, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(get_user_model(), db_column='owner',  on_delete=models.DO_NOTHING)
    def __str__(self):
        return u"title:%s, author:%s, abstract:%s, subject:%s" %(self.title, self.author, self.abstract, self.subject)

    class Meta:
        managed = True
        db_table = 'merterlibrary'
