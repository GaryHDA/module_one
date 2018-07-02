from django.contrib import admin
from .models import Beaches, Codes, All_Data, References, Finance, SLR_Beaches, SLR_Data, Projects, HDC_Beaches, HDC_Data
# Register your models here.

class BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']


admin.site.register(Beaches, BeachesAdmin)
admin.site.register(Projects, BeachesAdmin)

class SLR_BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']


admin.site.register(SLR_Beaches, SLR_BeachesAdmin)
# admin.site.register(Projects, BeachesAdmin)

class HDC_BeachesAdmin(admin.ModelAdmin):
    search_fields = ['location']


admin.site.register(HDC_Beaches, HDC_BeachesAdmin)


class All_DataAdmin(admin.ModelAdmin):

    raw_id_fields = ("location",)
    list_display=('date', 'location', 'item_code', 'item_description', 'item_material', 'quantity','project')


    fieldsets = ((None, {
    'fields':('date', 'location',
        'project', 'code', 'quantity', 'length')}),
        (None, {'fields':[]}))

    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material
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
    list_display=('date', 'location', 'item_code', 'item_description', 'item_material', 'quantity','project')


    fieldsets = ((None, {
    'fields':('date', 'location',
        'project', 'code', 'quantity')}),
        (None, {'fields':[]}))

    def item_code(self, obj):
        return obj.code.code
    def item_description(self, obj):
        return obj.code.description
    def item_material(self, obj):
        return obj.code.material

admin.site.register(HDC_Data, HDC_DataAdmin)


admin.site.site_header = "hammerdirt admin";
admin.site.site_title = "hammerdirt";
