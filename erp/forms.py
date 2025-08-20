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
            'cost_manufacturing_stone',
            'margin_stones',
            'note'
        ]
        widgets = {
            'lot_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'metal_full_name': forms.Select(attrs={'class': 'form-control'}),
            'master': forms.Select(attrs={'class': 'form-control'}),
            'cost_manufacturing_stone': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'margin_stones': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'lot_id': 'პარტიის N',
            'lot_date': 'თარიღი',
            'metal_full_name': 'მეტალი',
            'master': 'მასტერი',
            'cost_manufacturing_stone': 'ქვის ჩასმა',
            'margin_stones': 'მოგება ქვაზე',
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
            'cost_manufacturing_piece',
            'margin_piece',
            'note',
        ]
        widgets = {
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_piece': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_manufacturing_piece': forms.NumberInput(attrs={'class': 'form-control'}),
            'margin_piece': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'cost_piece': 'ქვის ღირებულება',
            'cost_manufacturing_piece': 'ჩასმის ფასი',
            'margin_piece': 'მოგება',
            'note': 'კომენტარი'
        }


class AddTransactionForm(forms.ModelForm):

    item = forms.ChoiceField(
        choices=lambda: [('', '-----------')] +
                        [('', '---ქვები---')] +
                        sorted([(s.stone_full_name, s.stone_full_name) for s in Stones.objects.all()]) +
                        [('', '---მეტალები---')] +
                        sorted([(m.metal_full_name, m.metal_full_name) for m in Metals.objects.all()]) +
                        [('', '---სხვა---')] +
                        sorted([(ms.label, ms.label) for ms in MaterialsServices.objects.all()]),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='მასალა/მომსახურება'
                            )

    class Meta:
        model = Transactions
        fields = [
            'tmstmp',
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
            'note',
        ]

        widgets = {
            'tmstmp': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'transaction_quantity': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'transaction_quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'pieces': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'stone_quality': forms.Select(attrs={'class': 'form-control'}),
            'cost_unit': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'image_location': forms.FileInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
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


class AddSinjiTransactionForm(forms.ModelForm):

    item = forms.ChoiceField(
        choices=lambda: [('', '---მეტალები---')] +
                        sorted([(m.metal_full_name, m.metal_full_name) for m in Metals.objects.all()]),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='აირჩიე მეტალი'
                            )

    transaction_type = forms.ModelChoiceField(
        queryset=TransactionTypes.objects.filter(label='გადაყვანა'),
        initial=TransactionTypes.objects.filter(label='გადაყვანა').first(),
        widget=forms.HiddenInput(),
        required=False,
        label=''
                                            )

    item_type = forms.ModelChoiceField(
        queryset=ItemTypes.objects.filter(label='მეტალი'),
        initial=ItemTypes.objects.filter(label='მეტალი').first(),
        widget=forms.HiddenInput(),
        required=False,
        label=''
                                        )

    transaction_quantity_unit = forms.ModelChoiceField(
        queryset=Units.objects.filter(label='გრამი'),
        initial=Units.objects.filter(label='გრამი').first(),
        widget=forms.HiddenInput(),
        required=False,
        label=''
                                                        )

    class Meta:
        model = Transactions
        fields = [
            'item',
            'item_type',
            'transaction_type',
            'transaction_quantity',
            'transaction_quantity_unit',
            'cost_unit',
            'description',
            'note',
        ]
        widgets = {
            'transaction_quantity': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'cost_unit': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'transaction_quantity': 'რაოდენობა',
            'cost_unit': 'ერთეულის ფასი',
            'description': 'იდენტიფიკატორი',
            'note': 'კომენტარი',
        }


class AddCastTransactionForm(forms.ModelForm):

    item = forms.ChoiceField(
        choices=lambda: [('', '-----------')] +
                        [('', '---მეტალები---')] +
                        sorted([(m.metal_full_name, m.metal_full_name) for m in Metals.objects.all()]) +
                        [('', '---მეტალის დანაკარგები---')] +
                        sorted([(m.metal_full_name + ' დანაკარგი', m.metal_full_name + ' დანაკარგი') for m in Metals.objects.all()]) +
                        [('', '---სხვა---')] +
                        [('ფული', 'ფული')] ,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='მეტალი/სხვა'
                            )

    transaction_type = forms.ModelChoiceField(
        queryset=TransactionTypes.objects.filter(label='ჩამოსხმა'),
        initial=TransactionTypes.objects.filter(label='ჩამოსხმა').first(),
        widget=forms.HiddenInput(),
        required=False,
        label=''
                                            )

    class Meta:
        model = Transactions
        fields = [
            'lot_id',
            'item',
            'item_type',
            'transaction_quantity',
            'transaction_quantity_unit',
            'cost_unit',
            'description',
            'note',
            'transaction_type',
        ]
        widgets = {
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_quantity': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'transaction_quantity_unit': forms.Select(attrs={'class': 'form-control'}),
            'cost_unit': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'lot_id': 'პარტიის N',
            'item_type': 'მეტალი ან ხელფასი',
            'transaction_type': 'ტრანზაქციის ტიპი',
            'transaction_quantity': 'რაოდენობა',
            'transaction_quantity_unit': 'ერთეული',
            'cost_unit': 'ერთეულის ფასი',
            'description': 'იდენტიფიკატორი',
            'note': 'კომენტარი',
            'pieces': 'ცალობა',
            'stone_quality': 'ხარისხი (ქვის)',
            'image_location': 'სურათი',
        }


class AddProcTransactionForm(AddCastTransactionForm):

    item = forms.ChoiceField(
        choices=lambda: [('', '-----------')] +
                        [('', '---მეტალები---')] +
                        sorted([(m.metal_full_name, m.metal_full_name) for m in Metals.objects.all()]) +
                        [('', '---სხვა---')] +
                        sorted([(ms.label, ms.label) for ms in MaterialsServices.objects.all()]),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='მასალა/მომსახურება'
                            )

    transaction_type = forms.ModelChoiceField(
        queryset=TransactionTypes.objects.filter(label='დამუშავება'),
        initial=TransactionTypes.objects.filter(label='დამუშავება').first(),
        widget=forms.HiddenInput(),
        required=False,
        label=''
                                            )