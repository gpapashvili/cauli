# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import decimal

from django.db import models
from django.utils.timezone import now
from django.db.models.functions import Concat
from django.db.models import F, ExpressionWrapper


def now_as_str():
    return now().strftime('%y-%m-%d-%H-%M-%S')


#########Simplest  lookup tables############
## this simple lookup tables don't need any database modifications
## do not need custom forms
## they will be controlled using django admin

class Units(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'units'
        ordering = ['label']
        verbose_name = 'ერთეული'
        verbose_name_plural = 'ერთეულები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class StoneNames(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stone_names'
        ordering = ['label']
        verbose_name = 'ქვის სახელი'
        verbose_name_plural = 'ქვის სახელები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class StoneQualities(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stone_qualities'
        ordering = ['label']
        verbose_name = 'ქვის ხარისხი'
        verbose_name_plural = 'ქვის ხარისხები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class Genders(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genders'
        ordering = ['label']
        verbose_name = 'სქესი'
        verbose_name_plural = 'სქესი'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class ModelCategories(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'model_categories'
        verbose_name = 'მოდელის კატეგორია'
        verbose_name_plural = 'მოდელის კატეგორიები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class Masters(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'masters'
        ordering = ['label']
        verbose_name = 'ხელოსანი'
        verbose_name_plural = 'ხელოსნები'
        db_table_comment = 'masters and other workers'

    def __str__(self):
        return f"{self.label}"


class TransactionTypes(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction_types'
        verbose_name = 'ტრანზაქციის ტიპი'
        verbose_name_plural = 'ტრანზაქციის ტიპები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class ItemTypes(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_types'
        verbose_name = 'საგნის ტიპი'
        verbose_name_plural = 'საგნის ტიპები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class MaterialsServices(models.Model):
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'materials_services'
        verbose_name = 'მასალა/მომსახურება'
        verbose_name_plural = 'მასალები/მომსახურებები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


#########Complicated  lookup tables that needs additional id############
## those complicated lookup tables need addition of django_id in database
## do not need custom forms
## will be managed using django admin


class Metals(models.Model):
    metal_name = models.CharField(null=False, blank=False)
    sinji = models.IntegerField(null=False, blank=False)
    # PostgreSQL currently implements only stored generated columns so db_persist=True
    metal_full_name = models.GeneratedField(expression=Concat('metal_name', "-",'sinji'),
                                            output_field=models.CharField(), db_persist=True, unique=True)
    note = models.TextField(blank=True, null=True)
    django_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'metals'
        ordering = ['metal_full_name']
        verbose_name = 'მეტალი'
        verbose_name_plural = 'მეტალები'
        db_table_comment = 'metals with sinjebi and their characteristics if any'

    def __str__(self):
        return f"{self.metal_full_name}"


class Stones(models.Model):
    stone_name = models.ForeignKey(StoneNames, models.DO_NOTHING, db_column='stone_name')
    size = models.CharField()
    size_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='size_unit', default='მილიმეტრი', related_name='stone_size_unit')
    weight = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    weight_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='weight_unit', default='კარატი', related_name='stone_weight_unit')
    stone_full_name = models.GeneratedField(expression=Concat('stone_name', "-", 'size'),
                                            output_field=models.CharField(), db_persist=True, unique=True)
    note = models.TextField(blank=True, null=True)
    django_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'stones'
        ordering = ['stone_name', 'size']
        verbose_name = 'ქვა'
        verbose_name_plural = 'ქვები'
        db_table_comment = 'stones and their characteristics'


    def __str__(self):
        return f"{self.stone_full_name}"


######################functional tables#################
## those functional tables do not need modification in database
## do not need custom forms
## can be managed using django admin


class Catalog(models.Model):

    def catalog_image_path(instance, filename):
        """Method to take model_id and file extension and return path to image file"""
        # Get the file extension
        ext = filename.split('.')[-1]
        # Generate filename as model_id.extension
        filename = f"{instance.model_id}.{ext}"
        # Return the complete path
        return f'catalog/{filename}'

    model_id = models.CharField(primary_key=True)
    creation_date = models.DateField(default=now)
    pieces = models.IntegerField(blank=True, null=True)
    model_name = models.CharField(blank=True, null=True)
    model_category = models.ForeignKey('ModelCategories', models.DO_NOTHING, db_column='model_category', blank=True, null=True)
    gender = models.ForeignKey('Genders', models.DO_NOTHING, db_column='gender', blank=True, null=True)
    image_location = models.ImageField(upload_to=catalog_image_path, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'catalog'
        ordering = ['model_id']
        verbose_name = 'კატალოგი'
        verbose_name_plural = 'კატალოგი'
        db_table_comment = 'catalog of products'

    def __str__(self):
        return f"{self.model_id}"


class Lots(models.Model):
    lot_id = models.AutoField(primary_key=True)
    lot_date = models.DateField(default=now)
    metal_full_name = models.ForeignKey('Metals', models.DO_NOTHING, db_column='metal_full_name', to_field='metal_full_name', blank=True, null=True)
    master = models.ForeignKey('Masters', models.DO_NOTHING, db_column='master', to_field='label', blank=True, null=True)
    cost_manufacturing_stone = models.DecimalField(max_digits=10, decimal_places=2)
    margin_stones = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    total_lot_weight = 0

    @property
    def models_count(self):
        return LotModels.objects.filter(lot_id=self.lot_id).count()

    @property
    def models_sold(self):
        return LotModels.objects.filter(lot_id=self.lot_id, sold=True).count()

    @property
    def total_stone_price(self):
        try:
            price = sum(LotModelStone.price for LotModelStone in LotModelStones.objects.filter(lot_id=self.lot_id))
        except:
            price = 'Err'
        return price

    @property
    def total_model_weight(self):
        try:
            weight = sum(lotmodel.weight for lotmodel in LotModels.objects.filter(lot_id=self.lot_id))
        except:
            weight = 'Err'
        return weight

    class Meta:
        managed = False
        db_table = 'lots'
        ordering = ['-lot_date', '-lot_id']
        verbose_name = 'პარტია'
        verbose_name_plural = 'პარტია'
        db_table_comment = 'lots info'

    def __str__(self):
        return f"{self.lot_id}"


######################Needs Custom Form#################
## those tables need modification in database
## those tables cannot be managed from django admin
## need custom forms


class CatalogStones(models.Model):
    model_id = models.ForeignKey('Catalog', models.CASCADE, db_column='model_id')
    stone_full_name = models.ForeignKey('Stones', models.DO_NOTHING, db_column='stone_full_name', to_field='stone_full_name')
    quantity = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    django_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'catalog_stones'
        ordering = ['model_id', 'stone_full_name']
        verbose_name = 'მოდელის ქვა'
        verbose_name_plural = 'მოდელის ქვები'
        db_table_comment = 'stones of models in catalog, only stones, but can be used for other if needed'

    def __str__(self):
        return f"{self.model_id}-{self.stone_full_name}"


class LotModels(models.Model):
    lot_id = models.ForeignKey('Lots', models.CASCADE, db_column='lot_id', to_field='lot_id')
    model_id = models.ForeignKey('Catalog', models.DO_NOTHING, db_column='model_id', to_field='model_id')
    tmstmp = models.CharField(primary_key=True, default=now_as_str)
    weight = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True)
    sold = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lot_models'
        ordering = ['-lot_id', '-tmstmp', 'model_id']
        verbose_name = 'პარტიის მოდელი'
        verbose_name_plural = 'პარტიის მოდელები'
        db_table_comment = 'models added to lot for production'

    def __str__(self):
        return f"{self.lot_id.lot_id}-{self.model_id}-{self.tmstmp}"


class LotModelStones(models.Model):
    lot_id = models.ForeignKey('Lots', models.CASCADE, db_column='lot_id', to_field='lot_id')
    model_id = models.ForeignKey('Catalog', models.DO_NOTHING, db_column='model_id', to_field='model_id')
    tmstmp = models.ForeignKey('LotModels', models.CASCADE, db_column='tmstmp', to_field='tmstmp')
    stone_full_name = models.ForeignKey('Stones', models.DO_NOTHING, db_column='stone_full_name', to_field='stone_full_name')
    quantity = models.IntegerField()
    # database triger will automatically fill weight and weight unit on stone_full_name change
    weight = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    weight_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='weight_unit', default='კარატი', related_name='lotmodelstone_weight_unit')
    cost_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_manufacturing_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margin_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.GeneratedField(expression=ExpressionWrapper( (F('cost_piece') + F('cost_manufacturing_piece') + F('margin_piece')) * F('quantity'),
                                                                output_field=models.DecimalField(max_digits=10, decimal_places=2) ),
                                  output_field=models.DecimalField(max_digits=10, decimal_places=2),
                                  db_persist=True, blank=True, null=True )
    note = models.TextField(blank=True, null=True)
    django_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'lot_model_stones'
        ordering = ['-lot_id', 'model_id', 'stone_full_name']
        verbose_name = 'პარტიის მოდელის ქვა'
        verbose_name_plural = 'პარტიის მოდელის ქვები'
        db_table_comment = 'stones of models in lot'


    def __str__(self):
        return f"{self.lot_id.lot_id}-{self.model_id}-{self.tmstmp.tmstmp}-{self.stone_full_name}"


class Transactions(models.Model):
    def image_path(instance, filename):
        """Method to take model_id and file extension and return path to image file"""
        ext = filename.split('.')[-1]
        filename = f"{instance.tmstmp}_{instance.item}.{ext}"
        return f'transactions/{filename}'

    tmstmp = models.CharField(primary_key=True, default=now_as_str)
    item = models.CharField()
    item_type = models.ForeignKey('ItemTypes', models.DO_NOTHING, db_column='item_type', related_name='transaction_item_type')
    transaction_type = models.ForeignKey('TransactionTypes', models.DO_NOTHING, db_column='transaction_type', related_name='transaction_transaction_type')
    description = models.CharField(blank=True, null=True)
    lot_id = models.ForeignKey('Lots', models.DO_NOTHING, db_column='lot_id', related_name='transaction_lot_id', blank=True, null=True)
    transaction_quantity = models.DecimalField(max_digits=10, decimal_places=4)
    transaction_quantity_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='transaction_quantity_unit', related_name='transaction_quantity_unit')
    pieces = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    stone_quality = models.ForeignKey('StoneQualities', models.DO_NOTHING, db_column='stone_quality', related_name='transaction_stone_quality', blank=True, null=True)
    cost_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.GeneratedField(expression=ExpressionWrapper(F('transaction_quantity') * F('cost_unit'),
                                                                    output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                       output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    cost_piece = models.GeneratedField(expression=ExpressionWrapper((F('transaction_quantity') * F('cost_unit')) / (F('pieces')),
                                                                    output_field=models.DecimalField(max_digits=10, decimal_places=2)),
                                       output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    image_location = models.ImageField(upload_to=image_path, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions'
        ordering = ['-tmstmp', 'item']
        verbose_name = 'ტრანზაქცია'
        verbose_name_plural = 'ტრანზაქციები'
        db_table_comment = 'all transactions related to material purchases, service purchases, sallary payments ...'

    def __str__(self):
        return f"{self.tmstmp}-{self.item}-{self.total_cost}"


# class Purchases(models.Model):
#     def image_path(instance, filename):
#         """Method to take model_id and file extension and return path to image file"""
#         ext = filename.split('.')[-1]
#         filename = f"{instance.tmstmp}_{instance.item}.{ext}"
#         return f'purchases/{filename}'
#
#     tmstmp = models.CharField(primary_key=True, default=now_as_str)
#     item = models.CharField()
#     purchase_id = models.CharField(blank=True, null=True)
#     purchase_quantity = models.DecimalField(max_digits=10, decimal_places=4)
#     purchase_quantity_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='purchase_quantity_unit', related_name='purchase_weight_unit')
#     pieces = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
#     stone_quality = models.ForeignKey('StoneQualities', models.DO_NOTHING, db_column='stone_quality', related_name='purchase_stone_quality', blank=True, null=True)
#     cost_unit = models.DecimalField(max_digits=10, decimal_places=2)
#     purchase_type = models.ForeignKey('TransactionTypes', models.DO_NOTHING, db_column='purchase_type', related_name='purchase_purchase_type')
#     total_cost = models.GeneratedField(expression=ExpressionWrapper( F('purchase_quantity')  * F('cost_unit'), output_field=models.DecimalField(max_digits=10, decimal_places=2) ),
#                                        output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
#     cost_piece = models.GeneratedField(expression=ExpressionWrapper( ( F('purchase_quantity')  * F('cost_unit') ) / ( F('pieces') ),
#                                                                          output_field=models.DecimalField(max_digits=10, decimal_places=2) ),
#                                        output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
#     image_location = models.ImageField(upload_to=image_path, null=True, blank=True)
#     note = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'purchases'
#         ordering = ['-tmstmp', 'item']
#         verbose_name = 'შესყიდვა'
#         verbose_name_plural = 'შესყიდვები'
#         db_table_comment = 'records of purchases for stones, metals and other items or services'
#
#     def __str__(self):
#         return f"{self.tmstmp}-{self.item}-{self.total_cost}"


##########################not yet determined###########################









##########################Doesn't work at all###########################

