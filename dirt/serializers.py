from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from dirt.models import AllData, Codes, Beaches, HDC_Data, HDC_Beaches

class SummarySerializer(serializers.Serializer):
    num_locs = serializers.IntegerField()
    total = serializers.IntegerField()
    num_samps = serializers.IntegerField()
    first = serializers.DateTimeField(format='%Y-%m-%d')
    last = serializers.DateTimeField(format='%Y-%m-%d')
    ave_dense = serializers.DecimalField(max_digits=11, decimal_places=4)
    max_dense = serializers.DecimalField(max_digits=11, decimal_places=4)
    min_dense = serializers.DecimalField(max_digits=11, decimal_places=4)
    two_five = serializers.DecimalField(max_digits=11, decimal_places=4)
    seven_five = serializers.DecimalField(max_digits=11, decimal_places=4)
    num_lakes = serializers.IntegerField()
    num_rivers = serializers.IntegerField()
    stan_dev = serializers.DecimalField(max_digits=11, decimal_places=4)
    location = serializers.CharField(max_length=100)



class MakeJson():
    def __init__(self, data):
        self.data = data
    def maker(data):
        return JSONRenderer().render(data.data)
class AllDataCreate(serializers.ModelSerializer):
    class Meta:
        model = AllData
        fields = ('location', 'date', 'length', 'quantity', 'code', 'project', 'owner')
class HdcDataCreate(serializers.ModelSerializer):
    class Meta:
        model = HDC_Data
        fields = ('location', 'date', 'length', 'quantity', 'code', 'project', 'owner')
class CitySerializer(serializers.Serializer):
    city = serializers.CharField()

class CodeSerial(serializers.ModelSerializer):
    class Meta:
        model = Codes
        fields = ('code', 'material', 'description', 'source')
class BeachSerial(serializers.Serializer):
    location = serializers.CharField(max_length=100)
    latitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    city = serializers.CharField(max_length=100)
    post = serializers.CharField(max_length=12)
    water = serializers.CharField(max_length=12)
    water_name = serializers.CharField(max_length=100,)
    project_id = serializers.CharField()
    owner = serializers.CharField()
class BeachCreate(serializers.ModelSerializer):
    class Meta:
        model = Beaches
        fields = ('location', 'latitude','longitude', 'city','post', 'water','water_name', 'project','owner')
class HdcBeachCreate(serializers.ModelSerializer):
    class Meta:
        model = HDC_Beaches
        fields = ('location', 'latitude','longitude', 'city','post', 'water','water_name', 'project','owner')


class AllDataSerial(serializers.Serializer):
    location_id = serializers.CharField()
    date = serializers.DateTimeField(format=None)
    code_id = serializers.CharField()
    length = serializers.IntegerField()
    quantity = serializers.IntegerField()
    project_id = serializers.CharField()
    owner = serializers.CharField()

class HdcDataSerial(serializers.Serializer):
    location_id = serializers.CharField()
    date = serializers.DateTimeField(format=None)
    code_id = serializers.CharField()
    length = serializers.IntegerField()
    quantity = serializers.IntegerField()
    project_id = serializers.CharField()
    owner = serializers.CharField()

class DailyTotalSerial(serializers.Serializer):
    location = serializers.CharField()
    date = serializers.DateTimeField(format=None)
    length = serializers.IntegerField()
    total = serializers.IntegerField()
    # density = serializers.DecimalField(max_digits=11, decimal_places=4)
    # project_id = serializers.CharField()

class DailyLogSerial(serializers.Serializer):
    dens_log = serializers.DecimalField(max_digits=11, decimal_places=4)

class DetailSerial(serializers.ModelSerializer):
    code = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = AllData
fields = ('location', 'date', 'length', 'quantity', 'code', 'project', )
