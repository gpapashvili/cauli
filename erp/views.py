import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from sqlalchemy import Engine
from .utils import create_db_engine, encrypt_password, decrypt_password
from django.contrib.auth import authenticate, login, logout

POSTGRESQL_ENGINE = None

# TODO: remove this is for debugging query
from django.db import connection


# Create your views here.

# completed views

# log in and log out

def login_db(request):
    """Connect to the database, required for pandas or other custom db access functions."""
    global POSTGRESQL_ENGINE

    if isinstance(POSTGRESQL_ENGINE, Engine):
        request.session['db_connected'] = True
        return POSTGRESQL_ENGINE
    elif request.session.get('username') and request.session.get('password'):
        POSTGRESQL_ENGINE = create_db_engine(decrypt_password(request.session.get('username')),
                                             decrypt_password(request.session.get('password')))
        if not isinstance(POSTGRESQL_ENGINE, Engine):
            request.session['db_connected'] = False
            messages.warning(request, POSTGRESQL_ENGINE)
            return redirect('login_user')
        else:
            request.session['db_connected'] = True
            messages.success(request, 'ბაზასთან წარმატებით დაკავშირდა.')
            return POSTGRESQL_ENGINE
    else:
        request.session['db_connected'] = False
        return redirect('login_user')


def logout_db(request):
    """Disconnect from the database and delete all credentials."""
    global POSTGRESQL_ENGINE
    POSTGRESQL_ENGINE = None
    request.session.delete('username')
    request.session.delete('password')
    request.session['db_connected'] = False
    return True


def login_user(request):
    """Log in user to the system and to the database to create sqlalchemy engine"""
    # to redirect to the requested page after login
    next_url = request.GET.get('next', 'home')
    # create db engine
    login_db(request)
    # if authenticated and a database is connected
    if request.user.is_authenticated and request.session.get('db_connected'):
        return redirect(next_url)
    # else if it is POST (you are trying to log in)
    elif request.method == 'POST':
        request.session['username'] = encrypt_password(request.POST['username'])
        request.session['password'] = encrypt_password(request.POST['password'])
        # Authenticate
        user = authenticate(request, username=decrypt_password(request.session.get('username')),
                                     password=decrypt_password(request.session.get('password')))
        # if a user is valid
        if user is not None:
            # connect to the system
            login(request, user)
            messages.success(request, "ავტორიზაცია წარმატებით დასრულდა.")
            # connect to database
            login_db(request)
            return redirect(next_url)
        # if user not valid
        else:
            messages.error(request, "პრობლემა სისტემაში შესვლისას!")
            return redirect('login_user')
    # open the page if not authenticated or not connected to db
    return render(request, 'login_user.html')


def logout_user(request):
    """Log out user from the system and from the database"""
    logout_db(request)
    logout(request)
    if not request.user.is_authenticated:
        messages.success(request, "სისტემიდან გამოსვლა წარმატებით დასრულდა")
    else:
        messages.success(request, f"მომხმარებელი {request.user.username} არ გამოსულა სისტემიდან")
    return redirect('login_user')


# in progress views

# catalog

from .utils import pd_query
from .models import Catalog
def catalog(request):
    login_db(request)
    all_models = Catalog.objects.all()
    stat = """SELECT cs.model_id, cs.stone_full_name, 
                s.weight * cs.quantity AS total_weight,
                s.weight, cs.quantity
              FROM catalog AS c
                LEFT JOIN catalog_stones AS cs ON c.model_id = cs.model_id
                LEFT JOIN stones AS s on cs.stone_full_name = s.stone_full_name"""
    all_model_stones = pd_query(stat, POSTGRESQL_ENGINE)
    return render(request, 'model_list.html', {'all_models': all_models, 'all_model_stones': all_model_stones})


from .forms import CatalogForm
def model_create(request):
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელი წარმატებით დაემატა.')
            return redirect('catalog')
    else:
        form = CatalogForm()
    return render(request, 'model_form.html', {'form': form, 'action': 'დამატება'})


from django.shortcuts import get_object_or_404
def model_update(request, model_id):
    model = get_object_or_404(Catalog, model_id=model_id)
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES, instance=model)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('catalog')
    else:
        form = CatalogForm(instance=model)
    return render(request, 'model_form.html', {'form': form, 'action': 'განახლება'})


def model_delete(request, model_id):
    model = get_object_or_404(Catalog, model_id=model_id)
    lot_ids = tuple(lot.lot_id.lot_id for lot in LotModels.objects.filter(model_id=model_id))
    if lot_ids:
        messages.error(request, f'მოდელი ვერ წაიშლება სანამ პარტია {lot_ids}-შია დამატებული!')
        return redirect('catalog')
    elif request.method == 'POST':
        model.delete()
        messages.success(request, 'მოდელი წარმატებით წაიშალა.')
        return redirect('catalog')
    return render(request, 'model_delete.html', {'model': model })


from .forms import CatalogStonesForm
def model_stone_add(request, model_id):
    if request.method == 'POST':
        form = CatalogStonesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელზე ქვა წარმატებით დაემატა.')
            return redirect('catalog')
    else:
        form = CatalogStonesForm()
        # will add default value to form when rendered
        form.fields['model_id'].widget.attrs['value'] = model_id
    return render(request, 'model_stone_add.html', {'form': form, 'model_id': model_id, 'action': 'დაამატე'})


from .models import CatalogStones
def model_stone_delete(request, model_id, stone_full_name):

    catalogstones = get_object_or_404(CatalogStones, model_id=model_id, stone_full_name=stone_full_name)

    if request.method == 'POST':
        catalogstones.delete()
        messages.success(request, 'მოდელზე ქვა წარმატებით წაშლილია.')
        return redirect('catalog')

    return render(request, 'model_stone_delete.html', {'catalogstones': catalogstones})


from .utils import insert_query
from .forms import LotListForm
def model_2_lot_add(request, model_id, lot_id):

    login_db(request)
    form = LotListForm()
    image_location = get_object_or_404(Catalog, model_id=model_id).image_location

    if request.method == 'POST':
        data = [{"lot_id": request.POST.get('select_lot_id'), "model_id": model_id}, ]
        insert_query('lot_models', data, POSTGRESQL_ENGINE)
        return redirect('catalog')
    elif lot_id != 0:
        data = [{"lot_id": lot_id, "model_id": model_id}, ]
        if insert_query('lot_models', data, POSTGRESQL_ENGINE):
            messages.success(request, f"მოდელი {model_id} წარმატებით დაემატა პარტიაში {lot_id}.")
        else:
            messages.error(request, f"მოდელი {model_id} ვერ დაემატა პარტიაში {lot_id}.")
        return redirect('lot_update', lot_id=lot_id)

    return render(request, 'model_2_lot_add.html', {'form': form, 'model_id': model_id, 'image_location':image_location})


# lot

from .models import Lots, Metals, Masters
def lot_list(request):
    login_db(request)
    weights = pd.DataFrame(pd_query("SELECT col_1, col_2 FROM total_final_per_lot", POSTGRESQL_ENGINE)).set_index('col_1')
    print(weights)
    lots = Lots.objects.all()
    for lot in lots:
        try:
            lot.total_lot_weight = weights.loc[lot.lot_id, 'col_2'] if weights.loc[lot.lot_id, 'col_2'] >=0 else 'Err'
        except:
            lot.total_lot_weight = 'Err'
    return render(request, 'lot_list.html', {'lots': lots})


from .forms import LotForm
def lot_create(request):
    if request.method == 'POST':
        lotform = LotForm(request.POST)
        if lotform.is_valid():
            lotform.save()
            messages.success(request, 'პარტია წარმატებით დაემატა.')
            return redirect('lot_list')
    else:
        lotform = LotForm()
    return render(request, 'lot_form.html', {'lotform': lotform, 'action': 'შექმენი'})


def lot_update(request, lot_id):
    login_db(request)
    lot = get_object_or_404(Lots, lot_id=lot_id)

    stat = f"""SELECT c.image_location, lm.model_id, lm.tmstmp, lm.sold, lm.weight
               FROM lot_models AS lm
                LEFT JOIN catalog AS c ON lm.model_id = c.model_id
               WHERE lm.lot_id = {lot_id}
               ORDER BY lm.sold, lm.tmstmp DESC, lm.model_id"""
    lot_models = pd_query(stat, POSTGRESQL_ENGINE)

    stat = f"""SELECT lms.model_id, lms.stone_full_name, lms.quantity, lms.weight, lms.tmstmp,
                    lms.cost_piece, lms.cost_manufacturing_piece, lms.margin_piece, lms.price,
                    lms.quantity * lms.weight AS total_weight,
                    lms.quantity * ( lms.cost_piece + lms.cost_manufacturing_piece + lms.margin_piece ) AS total_price
               FROM lot_model_stones AS lms
               WHERE lms.lot_id = {lot_id}
               ORDER BY lms.stone_full_name"""
    lot_stones = pd_query(stat, POSTGRESQL_ENGINE)

    if request.method == 'POST':
        lotform = LotForm(request.POST, instance=lot)
        if lotform.is_valid():
            lotform.save()
            messages.success(request, 'პარტიაზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('lot_list')
    else:
        lotform = LotForm(instance=lot)

    return render(request, 'lot_form.html', {'lotform': lotform, 'action': 'დაიმახსოვრე', 'lot_models':lot_models, 'lot_stones':lot_stones})


def lot_delete(request, lot_id):
    lot = get_object_or_404(Lots, lot_id=lot_id)
    if request.method == 'POST':
        lot.delete()
        messages.success(request, 'პარტია წარმატებით წაიშალა.')
        return redirect('lot_list')
    return render(request, 'lot_delete.html', {'lot': lot})


from .forms import LotModelsForm
def lot_model_update(request, lot_id, model_id, tmstmp):

    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)
    image_location = get_object_or_404(Catalog, model_id=model_id).image_location
    form = LotModelsForm(instance=lotmodel)

    if request.method == 'POST':
        form = LotModelsForm(request.POST, instance=lotmodel)
        if form.is_valid():
            form.save()
            messages.success(request, 'პარტიის მოდელზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('lot_update', lot_id=lot_id)
        else:
            messages.error(request, 'პრობლემა ინფორმაციის განახლებისას!')
    return render(request, 'lot_model_form.html', {'form': form, 'action': 'განახლება', 'image_location': image_location})


def lot_model_sold(request, lot_id, model_id, tmstmp, sold):

    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)
    lotmodel.sold = sold
    lotmodel.save()
    return redirect('lot_update', lot_id=lot_id)


from .models import LotModels
def lot_model_delete(request, lot_id, model_id, tmstmp):

    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)
    image_location = get_object_or_404(Catalog, model_id=model_id).image_location

    if request.method == 'POST':
        lotmodel.delete()
        messages.success(request, f'პარტია {lot_id}-ში მოდელი {model_id} წარმატებით წაშლილია.')
        return redirect('lot_update', lot_id=lot_id)

    return render(request, 'lot_model_delete.html', {'lot_id':lot_id, 'model_id':model_id, 'image_location':image_location})


from .forms import LotModelStonesForm
def lot_model_stone_add(request, lot_id, model_id, tmstmp):

    cost_manufacturing_piece = django_sql(f"""(SELECT cost_manufacturing_stone FROM lots WHERE lot_id = {lot_id})""")[0][0]
    margin_piece = django_sql(f"""(SELECT margin_stones FROM lots WHERE lot_id = {lot_id})""")[0][0]
    data = {'lot_id': lot_id, 'model_id': model_id, 'tmstmp': tmstmp}
    lot_model_stone = LotModelStones(lot_id=Lots.objects.get(lot_id=lot_id), model_id=Catalog.objects.get(model_id=model_id),
                                     tmstmp=LotModels.objects.get(tmstmp=tmstmp),
                                     cost_manufacturing_piece=cost_manufacturing_piece, margin_piece=margin_piece)
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        login_db(request)
        form = LotModelStonesForm(request.POST)
        data['stone_full_name'] = request.POST.get('stone_full_name')
        data['quantity'] = request.POST.get('quantity')
        data['cost_piece'] = request.POST.get('cost_piece') or None
        data['cost_manufacturing_piece'] = request.POST.get('cost_manufacturing_piece') or None
        data['margin_piece'] = request.POST.get('margin_piece') or None
        data['note'] = request.POST.get('note') or None
        data = [{k:v for k, v in data.items() if v is not None}]
        try:
            insert_query('lot_model_stones', data, POSTGRESQL_ENGINE)
        except Exception as e:
            messages.error(request, e)
        else:
            messages.success(request, f"N { lot_id } პარტიაში { model_id } მოდელზე მოდელზე ქვა {request.POST.get('stone_full_name')} წარმატებით დაემატა.")
        return redirect('lot_update', lot_id=lot_id )

    return render(request, 'lot_model_stone_form.html', {'form': form, 'action': 'დამატება', 'lot_id':lot_id}, )


from .utils import django_sql
def lot_model_stone_change(request, lot_id, model_id, tmstmp, stone_full_name):

    lot_model_stone = get_object_or_404(LotModelStones, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp, stone_full_name=stone_full_name)
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        login_db(request)
        cost_piece = django_sql(f"""(SELECT MAX(cost_piece) FROM transactions
                                        WHERE tmstmp > to_char(CURRENT_TIMESTAMP - '6 months'::INTERVAL, 'YY-MM-DD-HH24-MI-SS') 
                                        AND item = '{request.POST.get('stone_full_name')}')""")[0][0]
        cost_manufacturing_piece = django_sql(f"""(SELECT cost_manufacturing_stone FROM lots WHERE lot_id = {lot_id})""")[0][0]
        margin_piece = django_sql(f"""(SELECT margin_stones FROM lots WHERE lot_id = {lot_id})""")[0][0]

        stat = f"""UPDATE lot_model_stones
                    SET stone_full_name = '{request.POST.get('stone_full_name')}',
                    quantity = {request.POST.get('quantity')},
                    cost_piece = {request.POST.get('cost_piece') or cost_piece or "NULL"},
                    cost_manufacturing_piece = {request.POST.get('cost_manufacturing_piece') or cost_manufacturing_piece or "NULL"},
                    margin_piece = {request.POST.get('margin_piece') or margin_piece or "NULL"},
                    note = '{request.POST.get('note')}'
                   WHERE  lot_id={lot_id} AND model_id='{model_id}' AND tmstmp='{tmstmp}' AND stone_full_name='{stone_full_name}'"""
        try:
            crt_query(stat, POSTGRESQL_ENGINE)
        except Exception as e:
            messages.error(request, e)
        else:
            messages.success(request, f"N { lot_id } პარტიაში { model_id } მოდელზე მოდელზე ქვა {stone_full_name} შეიცვალა {request.POST.get('stone_full_name')} ქვით")
        return redirect('lot_update', lot_id=lot_id )

    return render(request, 'lot_model_stone_form.html', {'form': form, 'action': 'შეცვლა'}, )


from .models import LotModelStones
def lot_model_stone_delete(request, lot_id, model_id, tmstmp, stone_full_name):

    lotmodelstone = get_object_or_404(LotModelStones, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp, stone_full_name=stone_full_name)

    if request.method == 'POST':
        lotmodelstone.delete()
        messages.success(request, f'პარტია {lot_id}-ში მოდელ {model_id}-ზე წაიშალა {stone_full_name} !')
        return redirect('lot_update', lot_id=lot_id)

    return render(request, 'lot_model_stone_delete.html', {'lotmodelstone': lotmodelstone})


# transactions

from .models import Transactions
def transaction_list(request, transaction_type = 'ყველა გატარება', order_by='-tmstmp:transaction_type:lot_id:item'):

    login_db(request)
    # TODO: implement pagination later

    # TODO: implement sorting later
    order_by = [f"{field.replace('-', '')}  DESC" if '-' in field else field for field in order_by.split(':')]
    order_by = 'ORDER BY ' + ' , '.join(order_by)

    # filter by transaction_type
    where = f"transaction_type = '{transaction_type}'" if transaction_type != 'ყველა გატარება' else 'true'
    where = 'WHERE ' + where

    stat = f"""SELECT * FROM transactions {where} {order_by}"""
    transactions = pd_query(stat, POSTGRESQL_ENGINE)

    form = AddTransactionForm(request.POST) # request.POST needed to keep filter with previous filter values
    form.use_required_attribute = False # remove required tags for filter forms

    if request.method == 'POST' and len(transactions):
        fields = transactions[0].index
        for k, v in request.POST.items():
            if v != '' and k in fields or k in ['from', 'to']:
                if isinstance(v, (int, float)):
                    where += f" AND {k} = {v}"
                    # where.append(f"{k} = {v}")
                elif k == 'from_date' and v:
                    where += f" AND tmstmp > '{v[-8:]}-00-00-00'"
                    # where.append(f"tmstmp > '{v[-8:]}-00-00-00'")
                elif k == 'to_date' and v:
                    where += f" AND tmstmp < '{v[-8:]}-99-99-99'"
                    # where.append(f"tmstmp < '{v[-8:]}-99-99-99'")
                elif k == 'description' and v:
                    where += f" AND  {k} ILIKE '%{v}%'"
                    # where.append(f" {k} ILIKE '%{v}%'")
                elif k not in ['from_date', 'to_date']:
                    where += f" AND {k} = '{v}'"
                    # where.append(f"{k} = '{v}'")
        # where ="WHERE " + " AND ".join(where) if where else ""
        stat = f"""SELECT * FROM transactions {where} {order_by}"""
        print(stat)
        transactions = pd_query(stat, POSTGRESQL_ENGINE)

    totals = pd.DataFrame(transactions)

    return render(request, 'transaction_list.html', {'transactions': transactions, 'form': form, 'totals': totals, 'transaction_type':transaction_type})


from .forms import AddTransactionForm, AddSinjiTransactionForm, AddCastTransactionForm, AddProcTransactionForm
def transaction_create(request, transaction_type='ყველა გატარება'):
    # determine transaction type
    login_db(request)

    info_table = []

    tbl = [pd.Series({'col_1': 'მეტალები ჯამურად', 'col_2': 'სულ (გრამი)', 'col_3': 'ერთეულის ფასი (ლარი)','col_4': 'სულ ფასი (ლარი)'})]
    stat = """SELECT * FROM total_metals_per_metal"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [pd.Series({'col_1': 'სხვა მატერიალები ჯამურად', 'col_2': 'სულ (გრამი)', 'col_3': 'ერთეულის ფასი (ლარი)','col_4': 'სულ ფასი (ლარი)'})]
    stat = """SELECT * FROM total_other_materials"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [pd.Series( {'col_1': 'ბოლო 5 თარიღზე გადაყვანები', 'col_2': 'სულ აღებული (გრამი)', 'col_3': 'სულ დაბრუნებული (გრამი)', 'col_4': 'სხვაობა (უნდა იყოს 0)'})]
    stat = """SELECT * FROM total_sinji_per_date LIMIT 5"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [pd.Series( {'col_1': 'ბოლო 5 პარტიაზე ჩამოსხმები', 'col_2': 'ჩამოსხმული წონა (გრამი)', 'col_3': 'ჩამოსხმისას დანაკარგი (გრამი)',
                       'col_4': 'ჩამოსხმისას დანაკარგი (ლარი)', 'col_5': 'ჩამოსხმის ღირებულება (ლარი)'})]
    stat = """SELECT * FROM total_cast_per_lot LIMIT 5"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [pd.Series( {'col_1': 'ბოლო 5 პარტიაზე დამუშავება', 'col_2': 'დამუშავებული წონა (გრამი)', 'col_3': 'დამუშავებული ოქროს ფასი (ლარი)',
                       'col_4': 'დამუშავების დანაკარგი (გრამი)', 'col_5': 'დამუშავების დანაკარგი (გრამი)', 'col_6': 'ოქრომჭედლის მომს. საფ (ლარი)',
                       'col_7': 'სხვა ხარჯი (ლარი)'} ) ]
    stat = """SELECT * FROM total_final_per_lot LIMIT 5"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [pd.Series( {'col_1': 'ბოლო 5 პარტაზე მოდელების ჯამები', 'col_2': 'სულ წონა ბეჭდებიდან (გრამი)', 'col_3': 'სულ მოდელები (ცალი)', 'col_4': 'სულ ნაჭერი'} ) ]
    stat = """SELECT * FROM total_lot_model_per_lot LIMIT 5"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    tbl = [ pd.Series( {'col_1': 'ბოლო 5 პარტია', 'col_2': 'დამუშავებული წონა (გრამი)' , 'col_3': 'დამუშავებული ოქროს ფასი (ლარი)',
                        'col_4': 'სულ დანაკარგი (გრამი)', 'col_5': 'სულ დანაკარგი (ლარი)', 'col_6': 'ხელფასები და სხვა (ლარი)',
                        'col_7': 'სულ თვითღირებულება (ლარი)', 'col_8': 'თვითღირებულება გრამზე (ლარი)'} ) ]
    stat = """SELECT * FROM cost_calculation_per_lot LIMIT 5"""
    tbl.extend(pd_query(stat, POSTGRESQL_ENGINE))
    info_table.append(tbl)

    if transaction_type == 'გადაყვანა':
        Form = AddSinjiTransactionForm
    elif transaction_type == 'ჩამოსხმა':
        Form = AddCastTransactionForm
    elif transaction_type == 'დამუშავება':
        Form = AddProcTransactionForm
    else:
        Form = AddTransactionForm
        info_table = []

    form = Form()

    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
        print(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'ტრანზაქცია წარმატებით გატარდა.')
            return redirect('transaction_type', transaction_type)

    return render(request, 'transaction_form.html', {'form': form, 'info_table': info_table, 'transaction_type': transaction_type, 'action': 'დამატება'})


def transaction_delete(request, tmstmp, item):
    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'ტრანზაქცია წარმატებით წაიშალა.')
        return redirect('transaction_list')
    return render(request, 'transaction_delete.html', {'transaction': transaction})


def transaction_update(request, tmstmp, item, transaction_type='ყველა გატარება'):

    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)
    form = AddTransactionForm(instance=transaction)

    if request.method == 'POST':
        form = AddTransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'ტრანზაქციაზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('transaction_list')
        else:
            messages.error(request, 'პრობლემა ინფორმაციის განახლებისას!')

    return render(request, 'transaction_form.html', {'form': form, 'transaction_type': transaction_type, 'action': 'შეცვლა'})

# other

def home(request):
    # login to db in any view that uses pandas
    from cauli.settings import STATIC_ROOT, MEDIA_ROOT
    return render(request, 'home.html')


# TODO: ideas to add
# add database users


# not yet needed

from PIL.ImageStat import Global
from django.shortcuts import get_list_or_404
from .utils import crt_query
import os
from django.views.generic import TemplateView, DetailView, ListView
from .forms import CatalogListForm, ModelCategoryListForm, GenderListForm
