from django import forms
from .models import Catalog, ModelCategories, Genders, CatalogStones, Lots, LotModelStones


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
            'peaces',
            'model_name',
            'model_category',
            'gender',
            'image_location',
            'note',
        ]
        widgets = {
            'model_id': forms.TextInput(attrs={'class': 'form-control'}),
            'creation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'peaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'model_category': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_location': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'model_id': 'მოდელი',
            'creation_date': 'შექმნის თარიღი',
            'peaces': 'ნაჭერი',
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
            'quantity_unit',
            'note',
        ]
        widgets = {
            'model_id': forms.TextInput(attrs={'class': 'form-control'}),
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'model_id': 'მოდელის ნომერი',
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'quantity_unit': 'ერთეული (ცალი)',
            'note': 'კომენტარი'
        }


class LotForm(forms.ModelForm):
    class Meta:
        model = Lots
        fields = [
            'lot_id',
            'lot_date',
            'metal_full_name',
            'master_full_name',
            'note'
        ]
        widgets = {
            'lot_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'metal_full_name': forms.Select(attrs={'class': 'form-control'}),
            'master_full_name': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'lot_id': 'პარტიის N',
            'lot_date': 'თარიღი',
            'metal_full_name': 'მეტალი',
            'master_full_name': 'მასტერი',
            'note': 'კომენტარი'
        }


class LotModelStonesForm(forms.ModelForm):
    class Meta:
        model = LotModelStones
        fields = [
            'lot_id',
            'model_id',
            'tmstmp',
            'stone_full_name',
            'quantity',
            'quantity_unit',
            'note',
        ]
        widgets = {
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'model_id': forms.Select(attrs={'class': 'form-control'}),
            'tmstmp': forms.Select(attrs={'class': 'form-control'}),
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'lot_id': 'პარტიის ნომერი',
            'model_id': 'მოდელის ნომერი',
            'tmstmp': 'ტაგი დრო',
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'quantity_unit': 'ერთეული (ცალი)',
            'note': 'კომენტარი'
        }