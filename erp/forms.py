from importlib.metadata import requires

from django import forms
from .models import *


class CatalogListForm(forms.Form):
    select_model_id = forms.ModelChoiceField(
        queryset=Catalog.objects.all(),
        empty_label="აირჩიე მოდელი",
        widget=forms.Select,
        label='მოდელი',
        required=False,
    )


class ModelCategoryListForm(forms.Form):
    # ... your existing fields ...
    model_category = forms.ModelChoiceField(
        queryset=ModelCategories.objects.all(),
        empty_label="აირჩიე კატეგორია",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='კატეგორია',
        required=False,
    )


class GenderListForm(forms.Form):
    # ... your existing fields ...
    gender = forms.ModelChoiceField(
        queryset=Genders.objects.all(),
        empty_label="აირჩიე სქესი",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='სქესი',
        required=False,
    )


class LotListForm(forms.Form):
    select_lot_id = forms.ModelChoiceField(
        queryset=Lots.objects.all(),
        empty_label="აირჩიე პარტია",
        widget=forms.Select,
        label='პარტია',
        required=False,
    )


class CatalogForm(forms.ModelForm):
    class Meta:
        model = Catalog
        fields = [
            'model_id',
            'creation_date',
            'pieces',
            'model_name',
            'model_category',
            'gender',
            'image_location',
            'note',
        ]
        widgets = {
            'model_id': forms.TextInput(attrs={'class': 'form-control'}),
            'creation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pieces': forms.NumberInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'model_category': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_location': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'model_id': 'მოდელი',
            'creation_date': 'შექმნის თარიღი',
            'pieces': 'ნაჭერი',
            'model_name': 'სახელი',
            'model_category': 'კატეგორია',
            'gender': 'სქესი',
            'image_location': 'სურათი',
            'note': 'კომენტარი',
        }


class CatalogStonesForm(forms.ModelForm):
    class Meta:
        model = CatalogStones
        fields = [
            'model_id',
            'stone_full_name',
            'quantity',
            'note',
        ]
        widgets = {
            'model_id': forms.TextInput(attrs={'class': 'form-control'}),
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'model_id': 'მოდელის ნომერი',
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'note': 'კომენტარი'
        }


class LotForm(forms.ModelForm):
    class Meta:
        model = Lots
        fields = [
            'lot_id',
            'lot_date',
            'metal_full_name',
            'master',
            'note',
            'cost_manufacturing_stone',
            'margin_stones',
            'cost_grinding',
            'cost_polishing',
            'cost_plating',
            'cost_sinji',
        ]
        widgets = {
            'lot_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'metal_full_name': forms.Select(attrs={'class': 'form-control'}),
            'master': forms.Select(attrs={'class': 'form-control'}),
            'cost_grinding': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'cost_manufacturing_stone': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'cost_polishing': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'cost_plating': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'cost_sinji': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'margin_stones': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'lot_id': 'პარტიის N',
            'lot_date': 'თარიღი',
            'metal_full_name': 'მეტალი',
            'master': 'მასტერი',
            'cost_grinding': 'დამუშავება',
            'cost_manufacturing_stone': 'ქვის.ჩასმა',
            'cost_polishing': 'გაპრიალება',
            'cost_plating': 'როდირება',
            'cost_sinji': 'სინჯი',
            'margin_stones': 'მოგება.ქვაზე',
            'note': 'კომენტარი'
        }


class LotModelsForm(forms.ModelForm):
    class Meta:
        model = LotModels
        fields = [
            'sold',
            'lot_id',
            'model_id',
            'tmstmp',
            'weight',
            'note',
        ]
        widgets = {
            'sold': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'model_id': forms.Select(attrs={'class': 'form-control'}),
            'tmstmp': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'sold': 'გაყიდული',
            'lot_id': 'პარტიის ნომერი',
            'model_id': 'მოდელის ნომერი',
            'tmstmp': 'ტაგი დრო',
            'weight': 'ბეჭდის წონა',
            'note': 'კომენტარი',
        }


class LotModelStonesForm(forms.ModelForm):
    class Meta:
        model = LotModelStones
        fields = [
            'stone_full_name',
            'quantity',
            'cost_piece',
            'cost_manufacturing_stone',
            'margin_stones',
            'note',
        ]
        widgets = {
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_piece': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_manufacturing_stone': forms.NumberInput(attrs={'class': 'form-control'}),
            'margin_stones': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'cost_piece': 'ქვის ღირებულება',
            'cost_manufacturing_stone': 'ჩასმის ფასი',
            'margin_stones': 'მოგება',
            'note': 'კომენტარი'
        }


class AddTransactionForm(forms.ModelForm):

    class Meta:
        model = Transactions
        fields = [
            'transaction_type',
            'lot_id',
            'item',
            'item_type',
            'transaction_quantity',
            'transaction_quantity_unit',
            'cost_unit',
            'description',
            'pieces',
            'stone_quality',
            'image_location',
            'tmstmp',
            'note',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'tmstmp': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'transaction_quantity': forms.NumberInput(attrs={'class': 'form-control', 'size': 2, 'oninput': 'calculateTotalCost()', 'id':'transaction_quantity', }),
            'transaction_quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'pieces': forms.NumberInput(attrs={'class': 'form-control', 'size': 2, 'oninput': 'calculatePiecePrice()', 'id':'pieces', }),
            'stone_quality': forms.Select(attrs={'class': 'form-control'}),
            'cost_unit': forms.NumberInput(attrs={'class': 'form-control', 'size': 2, 'oninput': 'calculateTotalCost()', 'id':'cost_unit', }),
            'image_location': forms.FileInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'item': 'აქტივი',
            'tmstmp': 'ტრანზაქციის დრო',
            'item_type': 'მასალის/მომსახურების ტიპი',
            'transaction_type': 'ტრანზაქციის ტიპი',
            'description': 'იდენტიფიკატორი',
            'lot_id': 'პარტიის N',
            'transaction_quantity': 'რაოდენობა',
            'transaction_quantity_unit': 'ერთეული',
            'pieces': 'ცალობა',
            'stone_quality': 'ხარისხი (ქვის)',
            'cost_unit': 'ერთეულის ფასი',
            'image_location': 'სურათი',
            'note': 'კომენტარი',
        }
