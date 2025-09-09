from django import forms
from .models import Lots, Catalog, CatalogStones,LotModels, LotModelStones, Stones, Assets, Transactions, Customers, Metals


class LotListForm(forms.Form):
    select_lot_id = forms.ModelChoiceField(
        queryset=Lots.objects.all(),
        empty_label="აირჩიე პარტია",
        widget=forms.Select,
        label='პარტია',
        required=True,
    )


class MetalsForm(forms.ModelForm):
    class Meta:
        model = Metals
        fields = [
            'metal_name',
            'sinji',
            'note',
        ]
        widgets = {
            'metal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sinji': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'metal_name': 'მეტალი',
            'sinji': 'სინჯი',
            'note': 'კომენტარი',
        }


class StonesForm(forms.ModelForm):
    class Meta:
        model = Stones
        fields = [
            'stone_name',
            'size',
            'size_unit',
            'weight',
            'weight_unit',
            'note',
        ]
        widgets = {
            'stone_name': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'size_unit': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_unit': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'stone_name': 'ქვა',
            'size': 'ზომა',
            'size_unit': 'ზომის ერთეული',
            'weight': 'წონა',
            'weight_unit': 'წონის ერთეული',
            'note': 'კომენტარი',
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = [
            'full_name',
            'phone',
            'table_number',
            'id',
            'address',
            'note',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'table_number': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'id': forms.TextInput(attrs={'class': 'form-control', 'size': 2}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'size': 2, 'rows': 3}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'size': 2, 'rows': 4}),
        }
        labels = {
            'full_name': 'გვარი-სახელი',
            'phone': 'ტელეფონი',
            'table_number': 'დახლის N',
            'id': 'პირადი N',
            'address': 'მისამართი',
            'note': 'კომენტარი'
        }


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
            'price_gram_gold',
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
            'price_gram_gold': forms.NumberInput(attrs={'class': 'form-control', 'size': 2}),
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
            'price_gram_gold': 'გრ. ოქროს გასაყ. ფასი',
            'note': 'კომენტარი'
        }


class LotModelsForm(forms.ModelForm):
    class Meta:
        model = LotModels
        fields = [
            'lot_id',
            'model_id',
            'tmstmp',
            'weight',
            'cost_gram_gold',
            'price_gram_gold',
            'customer',
            'location',
            'sale_date',
            'note',
        ]
        widgets = {
            'lot_id': forms.Select(attrs={'class': 'form-control'}),
            'model_id': forms.Select(attrs={'class': 'form-control'}),
            'tmstmp': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'cost_gram_gold': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_gram_gold': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'lot_id': 'პარტიის ნომერი',
            'model_id': 'მოდელის ნომერი',
            'tmstmp': 'თარიღი',
            'weight': 'ბეჭდის წონა',
            'customer': 'მყიდველი',
            'sale_date': 'გაყიდვის თარიღი',
            'location': 'პროდუქტის მდებარეობა',
            'cost_gram_gold': 'გრ. ოქროს ღირებულება',
            'price_gram_gold': 'გრ. ოქროს გასაყიდი ფასი',
            'note': 'კომენტარი',
        }


class LotModelStonesForm(forms.ModelForm):
    class Meta:
        model = LotModelStones
        fields = [
            'installed',
            'stone_full_name',
            'quantity',
            'cost_piece',
            'cost_manufacturing_stone',
            'margin_stones',
            'note',
        ]
        widgets = {
            'installed': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'true'}),
            'stone_full_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_piece': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_manufacturing_stone': forms.NumberInput(attrs={'class': 'form-control'}),
            'margin_stones': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'installed': 'დაყენებული',
            'stone_full_name': 'ქვის სახელი და ზომა',
            'quantity': 'ქვების რაოდენობა მოდელში',
            'cost_piece': 'ქვის ღირებულება',
            'cost_manufacturing_stone': 'ჩასმის ფასი',
            'margin_stones': 'მოგება',
            'note': 'კომენტარი'
        }


class AddTransactionForm(forms.ModelForm):

    item = forms.ChoiceField(
        choices=lambda: [('', '-----------')] +
                        [('', '---ქვები---')] +
                        sorted([(s.stone_full_name, s.stone_full_name) for s in Stones.objects.all()]) +
                        [('', '---მეტალები---')] +
                        sorted([(m.metal_full_name, m.metal_full_name) for m in Metals.objects.all()]) +
                        sorted([(f'{m.metal_full_name} დანაკარგი', f'{m.metal_full_name} დანაკარგი') for m in Metals.objects.all()]) +
                        [('', '---სხვა---')] +
                        sorted([(ms.label, ms.label) for ms in Assets.objects.all()]),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='აქტივი'
                            )

    class Meta:
        model = Transactions
        fields = [
            'transaction_type',
            'lot_id',
            'customer',
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
            'customer': forms.Select(attrs={'class': 'form-control'}),
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
            'customer': 'კლიენტი',
            'transaction_quantity': 'რაოდენობა/თანხა',
            'transaction_quantity_unit': 'ერთეული',
            'pieces': 'ცალობა',
            'stone_quality': 'ხარისხი (ქვის)',
            'cost_unit': 'ერთეულის ფასი',
            'image_location': 'სურათი',
            'note': 'კომენტარი',
        }