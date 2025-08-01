from django.contrib import admin
from erp.models import *


# admin sites customization
admin.site.site_title = "კაულის ადმინის გვერდი"
admin.site.site_header = "კაულის ადმინი"
admin.site.index_title = ""


# Register your models here.


#########Simplest  lookup tables############


@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(Currencies)
class CurrenciesAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(StoneNames)
class StoneNamesAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(StoneQualities)
class StoneQualitiesAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(Genders)
class GendersAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(ModelCategories)
class ModelCategoriesAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(Masters)
class ModelCategoriesAdmin(admin.ModelAdmin):
    list_display = ["master_full_name", "note"]


#########Complicated  lookup tables that needs additional django_id############


@admin.register(Metals)
class MetalsAdmin(admin.ModelAdmin):
    list_display = ['full_name', "metal_name", "sinji", "note", 'django_id']

    def full_name(self, obj):
        return f"{obj.metal_name}-{obj.sinji}"
    full_name.short_description = "full_name"


@admin.register(Stones)
class StonesAdmin(admin.ModelAdmin):
    list_display = ['full_name', "stone_name", "size", 'size_unit', 'weight', 'weight_unit', "note", 'django_id']

    def full_name(self, obj):
        return f"{obj.stone_name}-{obj.size}"
    full_name.short_description = "full_name"


######################functional tables can be managed from admin but preferred to have custom form#################


@admin.register(Lots)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['lot_id', "lot_date", "metal_full_name", 'master_full_name', 'note']


# if you will edit model_id, django will create a new record with now model_id and leave the old one that you should delete manually
@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['model_id', "creation_date", "peaces", 'model_name', 'model_category', 'gender', 'image_location', 'note']


@admin.register(CatalogStones)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['model_id', "stone_full_name", "quantity", 'quantity_unit', 'note', 'django_id']


@admin.register(LotModels)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['lot_id', "model_id", "tmstmp", 'weight', 'weight_unit', 'note']


@admin.register(LotModelStones)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['lot_id', "model_id", "tmstmp", 'stone_full_name', 'quantity', 'quantity_unit', 'note', 'django_id']


######################can mot be managed from admin#################




##########################not yet determined###########################







