# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.utils.timezone import now
from django.db.models.functions import Concat
from django.db.models import F, ExpressionWrapper, Sum


def now_as_str():
    return now().strftime('%y-%m-%d-%H-%M-%S')


#########Simplest  lookup tables############
## this simple lookup tables don't need any database modifications
## do not need custom forms
## they will be controlled using django admin
## they are mostly used to have unique inputs


class Units(models.Model):
    """collection of all units for various fields"""
    objects = models.Manager()
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
    """only stone names, sizes are added in Stone table"""
    objects = models.Manager()
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
    """stone qualities"""
    objects = models.Manager()
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
    """for which gender is model created?"""
    objects = models.Manager()
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
    """What category is model? ring, airings, etc. """
    objects = models.Manager()
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
    """Master to whom is assigned lot"""
    objects = models.Manager()
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
    """types of transactions, ex: sale, purchase, processing, etc."""
    objects = models.Manager()
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
    """type or purpose of item in transactions table. ex: stone, metal, salary, income, etc."""
    objects = models.Manager()
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_types'
        verbose_name = 'აქტივის ტიპი/დანიშნულება'
        verbose_name_plural = 'აქტივის ტიპი/დანიშნულება'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class Assets(models.Model):
    """Used in transactions table for item field. Includes assets other than stone and metals. ex: money, stock, etc."""
    objects = models.Manager()
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assets'
        verbose_name = 'აქტივი'
        verbose_name_plural = 'აქტივები'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


class ProductLocation(models.Model):
    """Where is the product located? ex: safe, counter, seller(sold)."""
    objects = models.Manager()
    label = models.CharField(primary_key=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_location'
        verbose_name = 'პროდუქტის მდებარეობა'
        verbose_name_plural = 'პროდუქტის მდებარეობა'
        db_table_comment = 'lookup values'

    def __str__(self):
        return f"{self.label}"


#########Complicated  lookup tables that needs additional id############
## those complicated lookup tables need addition of django_id in database
## do not need custom forms
## will be managed using django admin


class Metals(models.Model):
    """combination of metal name and sinji (karat, purity)"""
    objects = models.Manager()
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
    """Combination of stone name and size, for diamonds size is also associated with weight in carat that is used later as a reference table"""
    objects = models.Manager()
    stone_name = models.ForeignKey('StoneNames', models.DO_NOTHING, db_column='stone_name')
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
## can be managed using django admin, but have their own management page


class Customers(models.Model):
    """list of customers, used in transactions and lotmodels tables"""
    objects = models.Manager()
    full_name = models.CharField(primary_key=True)
    phone = models.CharField(null=True, blank=True)
    table_number = models.CharField(null=True, blank=True)
    id = models.CharField(null=True, blank=True)
    address = models.CharField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    @property
    def count_models_owned(self):
        """return total number of models owned by customer calculated from LotModel"""
        return LotModels.objects.filter(customer=self.full_name).count()

    @property
    def count_transactions(self):
        """return count of records in Transactions"""
        return Transactions.objects.filter(customer=self.full_name).count()

    class Meta:
        managed = False
        db_table = 'customers'
        verbose_name = 'კლიენტი'
        verbose_name_plural = 'კლიენტები'
        db_table_comment = 'customer names and info'

    def __str__(self):
        return f"{self.full_name}"


class Catalog(models.Model):
    """list of model designs in the catalog, which will be copied to lotmodels when it is produced and can change characteristics."""
    objects = models.Manager()

    def catalog_image_path(self, filename):
        """Method to take model_id and file extension and return path to image file"""
        # Get the file extension
        ext = filename.split('.')[-1]
        # Generate filename as model_id.extension
        filename = f"{self.model_id}.{ext}"
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
    """Batch of models to produce"""
    objects = models.Manager()
    lot_id = models.AutoField(primary_key=True)
    lot_date = models.DateField(default=now)
    metal_full_name = models.ForeignKey('Metals', models.DO_NOTHING, db_column='metal_full_name', to_field='metal_full_name', blank=True, null=True)
    master = models.ForeignKey('Masters', models.DO_NOTHING, db_column='master', to_field='label', blank=True, null=True)
    cost_grinding = models.DecimalField(max_digits=10, decimal_places=2)
    cost_manufacturing_stone = models.DecimalField(max_digits=10, decimal_places=2)
    cost_polishing = models.DecimalField(max_digits=10, decimal_places=2)
    cost_plating = models.DecimalField(max_digits=10, decimal_places=2)
    cost_sinji = models.DecimalField(max_digits=10, decimal_places=2)
    margin_stones = models.DecimalField(max_digits=10, decimal_places=2)
    price_gram_gold = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)

    @property
    def models_count(self):
        """return number of models in lot"""
        return LotModels.objects.filter(lot_id=self.lot_id).count()

    @property
    def models_sold(self):
        """return number of models sold in lot, by location field"""
        return LotModels.objects.filter(lot_id=self.lot_id, location='გაყიდული').count()

    @property
    def total_lot_weight(self):
        """return total weight of all models in lot calculated from transaction records on lot"""
        return TPPL.objects.filter(lot_id=self.lot_id).first().total_weight_out or 0

    @property
    def total_model_weight(self):
        """return total weight of all models in lot calculated from LotModel.weight field"""
        result = LotModels.objects.filter(lot_id=self.lot_id).aggregate(
            total=Sum(F('weight'), default=0) )
        return result['total'] or 0

    @property
    def total_cost(self):
        """return total cost of all models in lot"""
        result = LUM.objects.filter(lot_id=self.lot_id).aggregate(
            total=Sum(F('model_cost'), default=0))
        return result['total'] or 0

    @property
    def total_price(self):
        """return total price of all models in lot"""
        result = LUM.objects.filter(lot_id=self.lot_id).aggregate(
            total=Sum(F('model_price'), default=0))
        return result['total'] or 0

    @property
    def total_margin(self):
        """return total cost of all stones in lot"""
        return self.total_price - self.total_cost

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
    """Stones assigned to models in the catalog"""
    objects = models.Manager()
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
    """Models added to lot for production. Db triggers will automatically add stones as assigned in catalog."""
    objects = models.Manager()
    lot_id = models.ForeignKey('Lots', models.CASCADE, db_column='lot_id', to_field='lot_id')
    model_id = models.ForeignKey('Catalog', models.DO_NOTHING, db_column='model_id', to_field='model_id')
    tmstmp = models.CharField(primary_key=True, default=now_as_str)
    weight = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True)
    customer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='customer', to_field='full_name', default='NA',)
    sale_date = models.DateField(blank=True, null=True)
    location = models.ForeignKey('ProductLocation', models.DO_NOTHING, db_column='location', default='სეიფი', to_field='label',)
    cost_gram_gold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_gram_gold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    model_gold_cost = models.GeneratedField(expression=ExpressionWrapper(F('cost_gram_gold') * F('weight'),
                                                                        output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                            output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    model_gold_price = models.GeneratedField(expression=ExpressionWrapper(F('price_gram_gold') * F('weight'),
                                                                        output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                             output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    note = models.TextField(blank=True, null=True)

    @property
    def image_location(self):
        """return image location of model from catalog table, needed for some pages"""
        return Catalog.objects.filter(model_id=self.model_id).first().image_location

    @property
    def model_cost(self):
        """return total cost of model calculated from db VIEW materialized in model LUM"""
        return LUM.objects.filter(tmstmp=self.tmstmp).first().model_cost

    @property
    def model_price(self):
        """return total price of model calculated from db VIEW materialized in model LUM"""
        return LUM.objects.filter(tmstmp=self.tmstmp).first().model_price

    @property
    def model_profit(self):
        """return total price of model calculated from db VIEW materialized in model LUM"""
        if self.model_price and self.model_cost:
            return self.model_price - self.model_cost
        else:
            return 0

    class Meta:
        managed = False
        db_table = 'lot_models'
        ordering = ['location', '-lot_id', 'model_id', 'weight', '-tmstmp']
        verbose_name = 'პარტიის მოდელი'
        verbose_name_plural = 'პარტიის მოდელები'
        db_table_comment = 'models added to lot for production'

    def __str__(self):
        return f"{self.lot_id.lot_id}-{self.model_id}-{self.tmstmp}"


class LotModelStones(models.Model):
    """Stones assigned to models in lot. DB trigger will automatically fill weight and weight unit on stone_full_name change"""
    objects = models.Manager()
    lot_id = models.ForeignKey('Lots', models.CASCADE, db_column='lot_id', to_field='lot_id')
    model_id = models.ForeignKey('Catalog', models.DO_NOTHING, db_column='model_id', to_field='model_id')
    tmstmp = models.ForeignKey('LotModels', models.CASCADE, db_column='tmstmp', to_field='tmstmp')
    stone_full_name = models.ForeignKey('Stones', models.DO_NOTHING, db_column='stone_full_name', to_field='stone_full_name')
    quantity = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    weight_unit = models.ForeignKey('Units', models.DO_NOTHING, db_column='weight_unit', default='კარატი', related_name='lotmodelstone_weight_unit')
    cost_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_manufacturing_stone = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margin_stones = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    installed = models.BooleanField(default=False)
    total_weight = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * F('weight'),
                                                                      output_field=models.DecimalField(max_digits=10,decimal_places=4)),
                                         output_field=models.DecimalField(max_digits=10, decimal_places=4), db_persist=True)
    total_cost_piece = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * F('cost_piece'),
                                                                          output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                             output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    total_cost_manufacturing_stone = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * F('cost_manufacturing_stone'),
                                                                                          output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                                           output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    total_cost = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * (F('cost_piece') + F('cost_manufacturing_stone')),
                                                                    output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                       output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    total_margin_stones = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * F('margin_stones'),
                                                                            output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                                output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
    total_price = models.GeneratedField(expression=ExpressionWrapper(F('quantity') * (F('cost_piece') + F('cost_manufacturing_stone') + F('margin_stones')),
                                                                    output_field=models.DecimalField(max_digits=10,decimal_places=2)),
                                       output_field=models.DecimalField(max_digits=10, decimal_places=2), db_persist=True)
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
    """Transactions (records) made in the system, ex: selling, buying, salary payments, asset usage and so on."""
    objects = models.Manager()

    def image_path(self, filename):
        """Method to take tmstmp, item and file extension and return path to image file"""
        ext = filename.split('.')[-1]
        filename = f"{self.tmstmp}_{self.item}.{ext}"
        return f'transactions/{filename}'

    tmstmp = models.CharField(default=now_as_str, blank=True, null=True)
    item = models.CharField()
    item_type = models.ForeignKey('ItemTypes', models.DO_NOTHING, db_column='item_type', related_name='transaction_item_type')
    transaction_type = models.ForeignKey('TransactionTypes', models.DO_NOTHING, db_column='transaction_type', related_name='transaction_transaction_type')
    description = models.CharField(blank=True, null=True)
    lot_id = models.ForeignKey('Lots', models.DO_NOTHING, db_column='lot_id', related_name='transaction_lot_id', blank=True, null=True)
    customer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='customer', blank=True, null=True)
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
    django_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'transactions'
        ordering = ['-tmstmp', 'item']
        verbose_name = 'ტრანზაქცია'
        verbose_name_plural = 'ტრანზაქციები'
        db_table_comment = 'all transactions related to material purchases, service purchases, sallary payments ...'

    def __str__(self):
        return f"{self.tmstmp}-{self.item}-{self.total_cost}"


######################views from database#################
## those are not tables but views that calculate some variables
## they are not managed or filled, but used for calculations

class CCPL(models.Model):
    """Calculates cost per gram for each lot, doesn't include stone costs"""
    objects = models.Manager()
    lot_id = models.IntegerField(primary_key=True)
    cost_per_gram = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'cost_calculation_per_lot'


class LUM(models.Model):
    """sums model weight and prices in lot with additional information for html table"""
    objects = models.Manager()
    tmstmp = models.CharField(primary_key=True)
    lot_id = models.IntegerField()
    model_price = models.DecimalField(max_digits=10, decimal_places=2)
    model_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'lot_update_models'


class TPPL(models.Model):
    """Total Weight of models from tranactions table, calculated from "metal" transaction records for lots"""
    objects = models.Manager()
    lot_id = models.IntegerField(primary_key=True)
    total_weight_out = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'total_processing_per_lot'


##########################not yet determined###########################

##########################Doesn't work at all###########################

