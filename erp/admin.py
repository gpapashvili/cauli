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
class MastersAdmin(admin.ModelAdmin):
    list_display = ["label", "note"]


@admin.register(TransactionTypes)
class TransactionTypesAdmin(admin.ModelAdmin):
    list_display = ['label', "note"]


@admin.register(ItemTypes)
class ItemTypesAdmin(admin.ModelAdmin):
    list_display = ['label', "note"]


@admin.register(Assets)
class AssetsAdmin(admin.ModelAdmin):
    list_display = ['label', "note"]


@admin.register(ProductLocation)
class ProductLocationAdmin(admin.ModelAdmin):
    list_display = ['label', "note"]


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customers._meta.fields]


#########Complicated  lookup tables that needs additional django_id############


@admin.register(Metals)
class MetalsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Metals._meta.fields]


@admin.register(Stones)
class StonesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Stones._meta.fields]


######################functional tables can be managed from admin but preferred to have custom form#################


@admin.register(Lots)
class LotsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lots._meta.fields]


# if you will edit model_id, django will create a new record with now model_id and leave the old one that you should delete manually
@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Catalog._meta.fields]


@admin.register(CatalogStones)
class CatalogStonesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CatalogStones._meta.fields]


@admin.register(LotModels)
class LotModelsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LotModels._meta.fields]


@admin.register(LotModelStones)
class LotModelStonesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LotModelStones._meta.fields]


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Transactions._meta.fields]


######################can mot be managed from admin#################




##########################not yet determined###########################








