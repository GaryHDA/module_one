from django.contrib import admin
from .models import Beaches, Codes, All_Data, References, Finance, SLR_Beaches, SLR_Data, Projects, HDC_Beaches, HDC_Data, Precious, Descente
import dirt.forms
import dirt.models as models
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django.contrib.auth.models import User

class BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']

admin.site.register(Beaches, BeachesAdmin)
admin.site.register(Projects, BeachesAdmin)

class SLR_BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']

admin.site.register(SLR_Beaches, SLR_BeachesAdmin)

class HDC_BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']

admin.site.register(HDC_Beaches, HDC_BeachesAdmin)


class All_DataAdmin(admin.ModelAdmin):

    raw_id_fields = ("location",)
    list_display=('date', 'location_name', 'item_code', 'quantity','project_project')
    list_filter = ('project__project',('location__city', DropdownFilter),('location__location',DropdownFilter))
    list_editable = ('quantity',)
    def formfield_for_dbfield(self,db_field,request,**kwargs):
        field = super(All_DataAdmin, self).formfield_for_dbfield(db_field, request,**kwargs)
        if db_field.name == 'location':
            field.initial = All_Data.objects.latest('date').location.location
        if db_field.name == 'project':
            field.initial = All_Data.objects.latest('date').project.project
        if db_field.name == 'length':
            field.initial = All_Data.objects.latest('date').length
        if db_field.name == 'date':
            field.initial = All_Data.objects.latest('date').date
        if db_field.name == 'owner':
            field.initial = User.username
        return field
    
    fields = (('date','project','location'),'length','code','quantity', 'owner')
    print(User.username)
    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material
    def project_project(self, obj):
        return obj.project.project

admin.site.register(All_Data, All_DataAdmin)

class ReferencesAdmin(admin.ModelAdmin):
    list_display = ('subject', 'title', 'abstract', 'author', 'project')
    list_filter = ('subject', 'author')

admin.site.register(References, ReferencesAdmin)
class CodesAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'material', 'source')
    list_filter = ('source', 'material')
admin.site.register(Codes, CodesAdmin)

class FinanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'entry', 'project', 'origin', 'amount')
    list_filter = ('project', 'entry', 'origin')
admin.site.register(Finance, FinanceAdmin)

class  HDC_DataAdmin(admin.ModelAdmin):

    raw_id_fields = ("location",)
    list_display=('date', 'location_name', 'item_code', 'quantity','project_project')
    list_filter = ('project__project',('location__city', DropdownFilter),('location__location',DropdownFilter))
    list_editable = ('quantity',)

    def formfield_for_dbfield(self,db_field,request,**kwargs):
        field = super(HDC_DataAdmin, self).formfield_for_dbfield(db_field, request,**kwargs)
        if db_field.name == 'location':
            field.initial = HDC_Data.objects.latest('date').location.location
        if db_field.name == 'project':
            field.initial = HDC_Data.objects.latest('date').project.project
        if db_field.name == 'length':
            field.initial = HDC_Data.objects.latest('date').length
        if db_field.name == 'date':
            field.initial = HDC_Data.objects.latest('date').date
        return field
    
    fields = (('date','project','location'),'length','code','quantity')

    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material
    def project_project(self, obj):
        return obj.project.project

admin.site.register(HDC_Data, HDC_DataAdmin)

class  P_DataAdmin(admin.ModelAdmin):
    
    raw_id_fields = ("location",)
    list_display=('date', 'location_name', 'item_code', 'quantity','project_project')
    list_filter = ('project__project',('location__city', DropdownFilter),('location__location',DropdownFilter))
    list_editable = ('quantity',)

    def formfield_for_dbfield(self,db_field,request,**kwargs):
        field = super(P_DataAdmin, self).formfield_for_dbfield(db_field, request,**kwargs)
        if db_field.name == 'location':
            field.initial = Precious.objects.latest('date').location.location
        if db_field.name == 'project':
            field.initial = Precious.objects.latest('date').project.project
        if db_field.name == 'length':
            field.initial = Precious.objects.latest('date').length
        if db_field.name == 'date':
            field.initial = Precious.objects.latest('date').date
        return field

    fields = (('date','project','location'),'length','code','quantity')

    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material
    def project_project(self, obj):
        return obj.project.project
    
admin.site.register(Precious, P_DataAdmin)

class  D_DataAdmin(admin.ModelAdmin):
    
    raw_id_fields = ("location",)
    list_display=('date', 'location_name', 'item_code', 'quantity','project_project')
    list_filter = ('project__project',('location__city', DropdownFilter),('location__location',DropdownFilter))
    list_editable = ('quantity',)

    def formfield_for_dbfield(self,db_field,request,**kwargs):
        field = super(D_DataAdmin, self).formfield_for_dbfield(db_field, request,**kwargs)
        if db_field.name == 'location':
            field.initial = Descente.objects.latest('date').location.location
        if db_field.name == 'project':
            field.initial = Descente.objects.latest('date').project.project
        if db_field.name == 'length':
            field.initial = Descente.objects.latest('date').length
        if db_field.name == 'date':
            field.initial = Descente.objects.latest('date').date
        return field

    fields = (('date','project','location'),'length','code','quantity')

    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material
    def project_project(self, obj):
        return obj.project.project
    
admin.site.register(Descente, D_DataAdmin)


admin.site.site_header = "hammerdirt admin";
admin.site.site_title = "hammerdirt";
