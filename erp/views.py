import pandas as pd
from django.shortcuts import render, redirect, reverse
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

from .models import Lots, Metals, Masters, Stones
def lot_list(request):
    login_db(request)
    weights = pd.DataFrame(pd_query("SELECT lot_id, total_weight_out FROM total_processing_per_lot", POSTGRESQL_ENGINE)).set_index('lot_id')
    lots = Lots.objects.all()
    for lot in lots:
        try:
            lot.total_lot_weight = weights.loc[lot.lot_id, 'total_weight_out'] if weights.loc[lot.lot_id, 'total_weight_out'] >=0 else 'Err'
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
               ORDER BY lm.sold, lm.model_id"""
    lot_models = pd_query(stat, POSTGRESQL_ENGINE)

    stat = f"""SELECT lms.model_id, lms.stone_full_name, lms.quantity, lms.weight, lms.tmstmp,
                    lms.cost_piece, lms.cost_manufacturing_stone, lms.margin_stones, lms.price,
                    lms.quantity * lms.weight AS total_weight,
                    lms.quantity * ( lms.cost_piece + lms.cost_manufacturing_stone + lms.margin_stones ) AS total_price
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

    cost_manufacturing_stone = django_sql(f"""(SELECT cost_manufacturing_stone FROM lots WHERE lot_id = {lot_id})""")[0][0]
    margin_stones = django_sql(f"""(SELECT margin_stones FROM lots WHERE lot_id = {lot_id})""")[0][0]
    data = {'lot_id': lot_id, 'model_id': model_id, 'tmstmp': tmstmp}
    lot_model_stone = LotModelStones(lot_id=Lots.objects.get(lot_id=lot_id), model_id=Catalog.objects.get(model_id=model_id),
                                     tmstmp=LotModels.objects.get(tmstmp=tmstmp),
                                     cost_manufacturing_stone=cost_manufacturing_stone, margin_stones=margin_stones)
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        login_db(request)
        form = LotModelStonesForm(request.POST)
        data['stone_full_name'] = request.POST.get('stone_full_name')
        data['quantity'] = request.POST.get('quantity')
        data['cost_piece'] = request.POST.get('cost_piece') or None
        data['cost_manufacturing_stone'] = request.POST.get('cost_manufacturing_stone') or None
        data['margin_stones'] = request.POST.get('margin_stones') or None
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
        cost_manufacturing_stone = django_sql(f"""(SELECT cost_manufacturing_stone FROM lots WHERE lot_id = {lot_id})""")[0][0]
        margin_stones = django_sql(f"""(SELECT margin_stones FROM lots WHERE lot_id = {lot_id})""")[0][0]

        stat = f"""UPDATE lot_model_stones
                    SET stone_full_name = '{request.POST.get('stone_full_name')}',
                    quantity = {request.POST.get('quantity')},
                    cost_piece = {request.POST.get('cost_piece') or cost_piece or "NULL"},
                    cost_manufacturing_stone = {request.POST.get('cost_manufacturing_stone') or cost_manufacturing_stone or "NULL"},
                    margin_stones = {request.POST.get('margin_stones') or margin_stones or "NULL"},
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


def lot_model_stone_default_update(request, lot_id, model_id, tmstmp, stone_full_name, field):

    login_db(request)
    message = 'ოპერაცია წარმატებით დასრულდა'

    where = f""" WHERE {field} IS NULL AND lot_id = {lot_id} """
    where += "" if model_id == 'all' else f""" AND model_id = '{model_id}' """
    where += "" if tmstmp == 'all' else f""" AND tmstmp = '{tmstmp}' """
    where += "" if stone_full_name == 'all' else f""" AND stone_full_name = '{stone_full_name}' """

    if field == 'cost_piece':
        stat = f"""SELECT * FROM transactions WHERE item = '{stone_full_name}'"""
        if pd_query(stat, POSTGRESQL_ENGINE):
            stat =f"""UPDATE lot_model_stones SET cost_piece = (SELECT MAX( cost_piece ) FROM transactions
                                                                WHERE tmstmp > to_char(CURRENT_TIMESTAMP - '6 months'::INTERVAL, 'YY-MM-DD-HH24-MI-SS')
                                                                AND item = '{stone_full_name}' GROUP BY item LIMIT 1) 
                      {where} """
            crt_query(stat, POSTGRESQL_ENGINE)
        else:
            message = f'{stone_full_name} არ არის ნაყიდი'
    elif field in ('cost_manufacturing_stone', 'margin_stones'):
        stat =f"""UPDATE lot_model_stones SET {field} = (SELECT {field} FROM lots
                                                         WHERE lot_id = {lot_id} LIMIT 1)
                  {where}"""
        crt_query(stat, POSTGRESQL_ENGINE)

    messages.success(request, message)

    # TODO: It Works implement in other views
    next_url = request.GET.get('next') or request.POST.get('next') or '/lot/'
    redirect_url = reverse('lot_stone_totals', kwargs={'lot_id': lot_id})
    redirect_url += f'?next={next_url}'
    return redirect(redirect_url)


def lot_stone_totals(request, lot_id=0):

    # TODO: do next_url for all other pages too
    next_url = request.GET.get('next')

    # TODO:
    login_db(request)

    summary_tables = []
    where_clause = f'lot_id = {lot_id}' if lot_id > 0 else f"lot_id > 0"
    header = 'პარტიაში დასამზადებელ (აუწონავ) მოდელებზე ქვების დაჯამებული სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'stone_full_name': 'ქვა', 'quantity': 'საჭირო რაოდ.', 'pieces': 'საწყობში',
                         'weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'transaction_quantity': 'საწყობში წონა', 'transaction_quantity_unit': 'ერთ.',
                         'cost_piece': 'ქვების ღირ.', 'avg_cost_piece': '1ც. საშ. ფასი', 'cost_manufacturing_stone': 'ჩასმის ღირ.', 'total_cost': 'სულ თვითღირ.',
                         'margin_stones': 'მოგება', 'price': 'ქვების გასაყ ფასი', })]
    stat = f"""SELECT * FROM lot_stone_validation_totals WHERE {where_clause} ORDER BY err DESC, lot_id DESC, stone_full_name"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})

    header = 'პარტიაში სულ ქვების დაჯამებული სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'stone_full_name': 'ქვა', 'quantity': 'საჭირო რაოდ.', 'pieces': 'საწყობში',
                         'weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'transaction_quantity': 'საწყობში წონა', 'transaction_quantity_unit': 'ერთ.',
                         'cost_piece': 'ქვების ღირ.', 'avg_cost_piece': '1ც. საშ. ფასი', 'cost_manufacturing_stone': 'ჩასმის ღირ.', 'total_cost': 'სულ თვითღირ.',
                         'margin_stones': 'მოგება', 'price': 'ქვების გასაყ ფასი', })]
    stat = f"""SELECT * FROM lot_stone_totals WHERE {where_clause} ORDER BY err DESC, lot_id DESC, stone_full_name"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})

    header = 'პარტიაში, მოდელების მოხედვით სულ ქვების დაუჯამებელი სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'model_id': 'მოდელი', 'stone_full_name': 'ქვა', 'quantity': 'რაოდ.',
                         'weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'cost_piece': 'ქვების ღირ.',
                         'cost_manufacturing_stone': 'ჩასმის ღირ.', 'total_cost': 'სულ თვითღირ.', 'margin_stones': 'მოგება', 'price': 'ქვების გასაყ ფასი', })]
    stat = f"""SELECT '' AS err, lot_id, model_id, stone_full_name, SUM(quantity), SUM(quantity * weight), weight_unit, SUM(quantity * cost_piece), 
                    SUM(quantity * cost_manufacturing_stone), SUM(quantity * (cost_piece + cost_manufacturing_stone)) AS cost_piece, 
                    SUM(quantity * margin_stones), SUM(quantity * price)
               FROM lot_model_stones WHERE {where_clause} GROUP BY lot_id , model_id , stone_full_name, weight_unit ORDER BY lot_id DESC , model_id , stone_full_name;"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})

    return render(request, 'lot_stone_totals.html',{'summary_tables': summary_tables, 'next_url': next_url })


# transactions

from .models import Transactions
def transaction_list(request, transaction_type = 'ნებისმიერი', order_by='-tmstmp:transaction_type:lot_id:item'):

    login_db(request)
    # TODO: implement pagination later

    # TODO: implement sorting later
    order_by = [f"{field.replace('-', '')}  DESC" if '-' in field else field for field in order_by.split(':')]
    order_by = 'ORDER BY ' + ' , '.join(order_by)

    # filter by transaction_type
    if transaction_type == 'ნებისმიერი':
        where = 'true'
    elif transaction_type == 'ლოტის გატარება':
        where = f"lot_id > 0"
    else:
        where = f"transaction_type = '{transaction_type}'"
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
                elif k == 'from_date' and v:
                    where += f" AND tmstmp > '{v[-8:]}-00-00-00'"
                elif k == 'to_date' and v:
                    where += f" AND tmstmp < '{v[-8:]}-99-99-99'"
                elif k == 'description' and v:
                    where += f" AND  {k} ILIKE '%{v}%'"
                elif k not in ['from_date', 'to_date']:
                    where += f" AND {k} = '{v}'"
        stat = f"""SELECT * FROM transactions {where} {order_by}"""
        transactions = pd_query(stat, POSTGRESQL_ENGINE)

    totals = pd.DataFrame(transactions)

    return render(request, 'transaction_list.html', {'transactions': transactions, 'form': form, 'totals': totals, 'transaction_type':transaction_type})


from .forms import AddTransactionForm
from django import forms
from .models import MaterialsServices
def transaction_create(request, transaction_identifier='ნებისმიერი', lot_id=0):

    login_db(request)
    ############create tables##################
    ###########################################
    # list of lot's transactions
    header = 'პარტიაზე გატარებების სია (მაქს. 30)'
    table = [pd.Series({'lot_id': 'პრტ.N', 'description':'იდენტიფიკატორი', 'tmstmp': 'თარიღი', 'transaction_type': 'ტრნზ.ტიპი',
                         'item': 'მსლ./მომსხ.', 'item_type': 'მასალის ტიპი', 'transaction_quantity': 'რაოდენობა', 'cost_unit': 'ერთ. ფასი',
                         'total_cost': 'სულ ფასი', 'act': '...'})]
    if transaction_identifier == 'გადაყვანა':
        where_clause = "transaction_type = 'გადაყვანა'"
    else:
        where_clause = f'lot_id = {lot_id}' if lot_id > 0 else f'lot_id > 0'
    stat = f"""SELECT * FROM records_for_summary WHERE {where_clause} ORDER BY lot_id DESC, tmstmp DESC LIMIT 30"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    transactions_table = {header: table}

    # create list of tables for metals, other and cash
    materials_tables = []
    header = 'მეტალების სია'
    table = [pd.Series({'item': 'მეტალები ჯამურად', 'total_quantity': 'სულ (გრამი)', 'cost_unit': 'ერთეულის ფასი','total_cost': 'სულ ფასი'})]
    stat = """SELECT * FROM total_metals_per_metal"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    materials_tables.append({header: table})
    header = 'სხვა მასალების სია'
    table = [pd.Series({'item': 'სხვა მატერიალები ჯამურად', 'total_quantity': 'სულ', 'cost_unit': 'ერთეულის ფასი','total_cost': 'სულ ფასი'})]
    stat = """SELECT * FROM total_other_materials"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    materials_tables.append({header: table})

    # summary tables
    summary_tables = []
    header = 'გადაყვანები'
    table = [pd.Series( {'transaction_date': 'ბოლო 5 თარიღზე გადაყვანები', 'total_weight_in': 'სულ გადასაყვანად (გრამი)',
                         'total_weight_out': 'სულ გადაყვანილი (გრამი)', 'total_weight_lost': 'დანაკარგი (გრამი)',
                         'cost_per_gram': 'გრამის ღირებულება'})]
    stat = """SELECT * FROM total_sinji_per_date LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # summary table for cast and processing
    header = 'ჩამოსხმები'
    table = [pd.Series( {'lot_id': 'ბოლო 5 პარტიაზე ჩამოსხმები', 'total_weight_in': 'სულ ჩამოსასხმელად (გრამი)', 'total_weight_out': 'სულ ჩამოსხმული (გრამი)',
                         'total_weight_lost': 'ჩამოსხმის დანაკარგი (გრამი)', 'total_cost_lost': 'ჩამოსხმის დანაკარგი (ლარი)',
                         'total_cost': 'ჩამოსხმის ღირებულება', 'total_salary': 'აქედან ხელფასი'})]
    stat = """SELECT * FROM total_cast_per_lot LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    header = 'დამუშავებები'
    table = [pd.Series( {'lot_id': 'ბოლო 5 პარტიაზე დამუშავება', 'total_weight_in': 'სულ დასამუშავებელი (გრამი)',
                         'total_weight_out': 'სულ დამუშავებული (გრამი)', 'total_cost_out': 'სულ დამუშავებული (ლარი)',
                         'total_weight_lost': 'დამუშავების დანაკარგი (გრამი)', 'total_cost_lost': 'დამუშავების დანაკარგი (ლარი)',
                         'total_cost': 'დამუშავების ღირებულება', 'total_salary': 'აქედან ხელფასი'} ) ]
    stat = """SELECT * FROM total_processing_per_lot LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # finals summary table
    header = 'პარტიის მოდელებზე მონაცემები'
    table = [pd.Series( {'lot_id': 'ბოლო 5 პარტაზე მოდელების ჯამები', 'total_weight_models': 'სულ წონა ბეჭდებიდან (გრამი)',
                         'model_count': 'მოდელების რაოდენობა (ცალი)', 'pieces_sum': 'ნაჭრების ჯამი'} ) ]
    stat = """SELECT * FROM total_lot_model_per_lot LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # salary table
    header = 'ხელფასები'
    table = [pd.Series( {'lot_id': 'ბოლო 5 პარტაზე ხელფასები', 'cost_casting': 'ჩამოსხმა', 'cost_grinding': 'დამუშავება',
                         'cost_manufacturing_stone': 'თვლის ჩასმა', 'cost_polishing': 'გაპრიალება',
                         'cost_plating': 'როდირება', 'cost_sinji': 'სინჯი', 'total_salary': 'სულ'} ) ]
    stat = """SELECT * FROM salaries_per_lot LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # gold cost calculation
    header = 'საბოლოო ჯამები'
    table = [ pd.Series( {'lot_id': 'ბოლო 5 პარტია', 'total_weight_out': 'დამუშავებული ოქროს წონა (გრამი)', 'total_cost_out': 'დამუშავებული ოქროს ფასი',
                          'total_weight_lost': 'სულ დანაკარგი (გრამი)', 'total_cost_lost': 'სულ დანაკარგი (ლარი)',
                          'total_salary_other_cost': 'ხელფასები და სხვა', 'total_cost': 'სულ თვითღირებულება',
                          'cost_per_gram': 'გრამის თვითღირებულება'} ) ]
    stat = """SELECT * FROM cost_calculation_per_lot LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    ###########################################
    ############create tables##################

    ##############create form##################
    ###########################################
    if lot_id:
        initial = {'lot_id': lot_id}
        hidden_fields = ['lot_id']
        metal_full_name = Lots.objects.get(lot_id=lot_id).metal_full_name
        metals = [['', '---მეტალები---']] + [[f'{metal_full_name}', f'{metal_full_name}']]
        metal_lost = [[f'{metal_full_name} დანაკარგი', f'{metal_full_name} დანაკარგი']]
    else:
        initial = {}
        hidden_fields = []
        metals = [['', '---მეტალები---']] + sorted([([o.metal_full_name] * 2) for o in Metals.objects.all()])
        # metal_lost = [['', '---მეტალის დანაკარგები---']] + sorted([([o.metal_full_name] * 2) for o in Metals.objects.all()])
    stones = [['', '---ქვები---']] + sorted([([o.stone_full_name] * 2) for o in Stones.objects.all()])
    other_items = [['', '---სხვა---']] + sorted([([o.label] * 2) for o in MaterialsServices.objects.all()])

    match transaction_identifier:
        case 'გადაყვანა':
            initial.update({'transaction_type': 'გადაყვანა', 'item_type': 'მეტალი', 'transaction_quantity_unit': 'გრამი'})
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location'])
        case 'ქვის_შესყიდვა':
            initial.update({'transaction_type': 'შესყიდვა', 'item_type': 'ქვა',})
            item_choices = stones
            item_label = 'აირჩიე ქვა'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id'])
        case 'მეტალის_შესყიდვა':
            initial.update({'transaction_type': 'გადაყვანა', 'item_type': 'მეტალი', 'transaction_quantity_unit': 'გრამი'})
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location'])
        case 'ჩამოსხმა' | 'დამუშავება':
            initial.update({'lot_id': lot_id, 'transaction_type': 'ჩამოსხმა'})
            item_choices = metals + metal_lost + other_items
            item_label = 'აირჩიე მეტალი/მეტალის დანაკარგი/ფული'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location'])
        case 'მეტალის_აღება' | 'მეტალის_დაბრუნება':
            initial.update({'lot_id': lot_id, 'transaction_type': 'დამუშავება' if 'დამუშავება' in request.GET.get('next', 'დამუშავება') else 'ჩამოსხმა',
                            'item': metal_full_name, 'item_type': 'მეტალი',
                            'transaction_quantity_unit': 'გრამი',
                            'description': ' '.join([str(metal_full_name), transaction_identifier.split('_')[1],
                                                     ' საწყობიდან' if transaction_identifier == 'მეტალის_აღება' else ' საწყობში' ] ) } )
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location'])
        case 'მეტალის_დანაკარგი':
            initial.update({'lot_id': lot_id, 'transaction_type': 'დამუშავება' if 'დამუშავება' in request.GET.get('next', 'დამუშავება') else 'ჩამოსხმა',
                            'item': f'{metal_full_name} დანაკარგი', 'item_type': 'მეტალი',
                            'transaction_quantity_unit': 'გრამი',
                            'description': 'დანაკარგი' } )
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location'])
        case 'ხელფასი':
            initial.update({'lot_id': lot_id, 'transaction_type': 'დამუშავება' if 'დამუშავება' in request.GET.get('next', 'დამუშავება') else 'ჩამოსხმა',
                            'item': 'ფული', 'item_type': 'მომსახურება',  } )
            item_choices =  other_items + metals + stones
            item_label = 'ფული'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location'])
        case _:
            item_choices = metals + other_items + stones
            item_label = 'აქტივი'

    form = AddTransactionForm(initial=initial)
    form.fields['item'] = forms.ChoiceField(choices=item_choices, widget=forms.Select(attrs={'class': 'form-control'}),  label=item_label)
    for field in hidden_fields:
        form.fields[field].widget = forms.HiddenInput()
        form.fields[field].label = ''
    ###########################################
    ##############create form##################

    next_url = f'/lot/{lot_id}/update/' if lot_id else '/transaction_list/'
    next_url = request.GET.get('next') or request.POST.get('next') or next_url

    if request.method == 'POST':

        form = AddTransactionForm(request.POST, request.FILES)
        if form.is_valid():

            # validate sign of quantity based on from or out of stock
            if (transaction_identifier in ('მეტალის_აღება', 'ხელფასი')):
                value = -abs(form.cleaned_data['transaction_quantity'])
            elif (transaction_identifier in ('მეტალის_დაბრუნება', 'მეტალის_დანაკარგი')):
                value = abs(form.cleaned_data['transaction_quantity'])
            else:
                value = form.cleaned_data['transaction_quantity']

            instance = form.save(commit=False)
            instance.transaction_quantity = value

            form.save()
            messages.success(request, 'ტრანზაქცია წარმატებით გატარდა.')

            # next_url = request.GET.get('next') or request.POST.get('next') or '/transaction_list/'
            if transaction_identifier in ('მეტალის_აღება', 'მეტალის_დაბრუნება', 'მეტალის_დანაკარგი', 'ხელფასი'):
                return redirect('lot_update', lot_id=lot_id)
            elif lot_id:
                redirect_url = reverse('transaction_create', kwargs={'transaction_identifier': transaction_identifier, 'lot_id': lot_id})
            else:
                redirect_url = reverse('transaction_type', kwargs={'transaction_type': transaction_identifier})

            redirect_url += f'?next={next_url}'
            return redirect(redirect_url)
        else:
            messages.error(request, 'შეცდომაა ტრანზაქციის შესრულებისას')

    return render(request, 'transaction_form.html', {'form': form, 'transaction_identifier': transaction_identifier, 'action': 'დამატება',
                                                                         'materials_tables': materials_tables, 'summary_tables': summary_tables,
                                                                         'transactions_table': transactions_table, 'next_url': next_url, })


def transaction_delete(request, tmstmp, item):
    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)

    next_url = f'/lot/{transaction.lot_id}/update/' if transaction.lot_id else '/transaction_list/'
    next_url = request.GET.get('next') or request.POST.get('next') or next_url

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'ტრანზაქცია წარმატებით წაიშალა.')

        # next_url = request.GET.get('next') or request.POST.get('next') or '/transaction_list/'
        # redirect_url = reverse('transaction_list')
        # redirect_url += f'?next={next_url}'

        return redirect(next_url)
        # return redirect('transaction_list')
    return render(request, 'transaction_delete.html', {'transaction': transaction, 'next_url': next_url})


def transaction_update(request, tmstmp, item, transaction_identifier='ნებისმიერი'):

    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)
    form = AddTransactionForm(instance=transaction)

    next_url = '/transaction_list/' if transaction.lot_id == 0 else f'/lot_update/{transaction.lot_id}/update/'
    next_url = request.GET.get('next') or request.POST.get('next') or next_url

    if request.method == 'POST':
        form = AddTransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'ტრანზაქციაზე ინფორმაცია წარმატებით განახლდა.')

            redirect_url = reverse('transaction_list')
            redirect_url += f'?next={next_url}'

            return redirect(redirect_url)
            # return redirect('transaction_list')
        else:
            messages.error(request, 'პრობლემა ინფორმაციის განახლებისას!')

    return render(request, 'transaction_form.html', {'form': form, 'transaction_identifier': transaction_identifier, 'action': 'შეცვლა', 'next_url': next_url})


from time import sleep
def auto_salary(request, lot_id):

    login_db(request)
    # list of lot's transactions
    header = 'პარტიაზე უკვე გადახდილი ხელფასები '
    table = [pd.Series({'lot_id': 'პრტ.N', 'description':'იდენტიფიკატორი', 'tmstmp': 'თარიღი', 'transaction_type': 'ტრნზ.ტიპი',
                         'item': 'მსლ./მომსხ.', 'item_type': 'მასალის ტიპი', 'transaction_quantity': 'რაოდენობა', 'cost_unit': 'ერთ. ფასი',
                         'total_cost': 'სულ ფასი', 'act': '...'})]
    stat = f"""SELECT * FROM records_for_summary WHERE lot_id = {lot_id} AND item_type = 'მომსახურება' ORDER BY lot_id DESC, tmstmp DESC LIMIT 30"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    transactions_table = {header: table}

    salaries = pd_query(f"""SELECT * FROM salaries_per_lot WHERE lot_id = '{lot_id}'""", POSTGRESQL_ENGINE)[0]
    prices = pd_query(f"""SELECT * FROM lots WHERE lot_id = '{lot_id}'""", POSTGRESQL_ENGINE)[0]
    units = {'cost_grinding': 'გრამი', 'cost_manufacturing_stone': 'ცალი', 'cost_polishing': 'ნაჭერი', 'cost_plating': 'ნაჭერი', 'cost_sinji': 'ნაჭერი'}
    descriptions = {'cost_grinding': 'დამუშავების', 'cost_manufacturing_stone': 'თვლის ჩასმის', 'cost_polishing': 'გაპრიალების',
                    'cost_plating': 'როდირების', 'cost_sinji': 'სინჯის'}

    if request.method == 'POST':
        salary_list = request.POST.getlist('salary_list')

        for salary_type in salary_list:
            data = {'lot_id': lot_id, 'transaction_type': 'დამუშავება', 'item': 'ფული', 'item_type': 'მომსახურება', }
            data['transaction_quantity'] = float(salaries[salary_type] / prices[salary_type]) * -1
            data['cost_unit'] = prices[salary_type]
            data['transaction_quantity_unit'] = units[salary_type]
            data['description'] = f'{descriptions[salary_type]} გადასახადი'
            data = [data]
            try:
                insert_query('transactions', data, POSTGRESQL_ENGINE)
            except Exception as e:
                messages.error(request, f'პრობლემა {e} {data[0]['description']} ხელფასების შეყვანისას.')
            else:
                messages.success(request, f'{data[0]['description']} გატარება წარმატებით გატარდა.')
        return redirect('auto_salary', lot_id)

        # return redirect('auto_salary.html', transaction_identifier=transaction_identifier, lot_id=lot_id)
    return render(request, 'auto_salary.html', {'transactions_table': transactions_table, 'lot_id' : lot_id, 'salaries': salaries})

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
