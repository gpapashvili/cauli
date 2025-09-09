from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.forms import modelform_factory, HiddenInput, ChoiceField, Select, TextInput, Textarea
from sqlalchemy import Engine
import pandas as pd
from django.utils.timezone import now
from .utils import create_db_engine, encrypt_password, decrypt_password, insert_query, pd_query, django_sql, crt_query
from .models import (Lots, Metals, Stones, Catalog, CatalogStones, LotModelStones, LotModels, Customers, Units, StoneNames, StoneQualities,
                     Genders, ModelCategories, Masters, TransactionTypes, ItemTypes, Assets, ProductLocation, Transactions)
from .forms import (LotForm, LotModelsForm, LotListForm, CatalogStonesForm, CatalogForm, LotModelStonesForm, CustomerForm,
                    MetalsForm, StonesForm, AddTransactionForm)

POSTGRESQL_ENGINE = None


# Create your views here.

# completed views

######################## log in and log out ###########################


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


######################## catalog ###########################


def catalog(request):
    """contains a list of models and stones with totals in the header"""
    login_db(request)
    # will get models from db view, not django model.
    models = pd_query(f'SELECT * FROM catalog ORDER BY model_id', POSTGRESQL_ENGINE)
    # get all stones for models
    stat = f"""SELECT cs.model_id, cs.stone_full_name, s.weight * cs.quantity AS total_weight, s.weight, cs.quantity
               FROM catalog AS c
                LEFT JOIN catalog_stones AS cs ON c.model_id = cs.model_id
                LEFT JOIN stones AS s on cs.stone_full_name = s.stone_full_name
               ORDER BY cs.stone_full_name"""
    stones = pd.DataFrame(pd_query(stat, POSTGRESQL_ENGINE))
    # some statistical information from produced models
    statistics = pd.DataFrame(pd_query(f"""SELECT model_id, AVG(weight) AS avg_weight, AVG(model_cost) AS avg_cost, AVG(model_price) AS avg_price
                                                FROM lot_update_models GROUP BY model_id""", POSTGRESQL_ENGINE))
    # add stones information as list of pandas series using sql query. some statistics can be added too
    for model in models:
        model['stones'] = [row for _, row in stones[stones.model_id == model.model_id].iterrows()]
        if not statistics[statistics.model_id == model.model_id].empty:
            model['avg_weight'] = statistics[statistics.model_id == model.model_id].iat[0, 1]
            model['avg_price'] = statistics[statistics.model_id == model.model_id].iat[0, 2]
            model['avg_cost'] = statistics[statistics.model_id == model.model_id].iat[0, 3]
            model['avg_profit'] = model['avg_price'] -  model['avg_cost']

    # calculate totals for header
    totals = pd.Series()
    totals_temp = pd.DataFrame(models)
    if not totals_temp.empty:
        totals['image_count'] = totals_temp['image_location'].count()
        totals['model_count'] = totals_temp['model_id'].count()
        totals['name_count'] = totals_temp['model_name'].count()
        totals['total_pieces'] = totals_temp['pieces'].sum()
        totals['model_category_count'] = totals_temp['model_category'].count()

    return render(request, 'model_list.html', {'all_models': models, 'totals':totals})


def model_create(request):
    """create a new model in catalog using dedicated form"""
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელი წარმატებით დაემატა.')
            return redirect('catalog')
        else:
            messages.error(request, f'შეცდომა {form.errors} მოდელის დამატებისას')
    else:
        form = CatalogForm()
    return render(request, 'model_form.html', {'form': form, 'action': 'დამატება'})


def model_update(request, model_id):
    """update a model in catalog using dedicated form"""
    model = get_object_or_404(Catalog, model_id=model_id)
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES, instance=model)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('catalog')
        else:
            messages.error(request, f'შეცდომა {form.errors} მოდელის განახლებისას')
    else:
        form = CatalogForm(instance=model)
    return render(request, 'model_form.html', {'form': form, 'action': 'განახლება'})


def model_delete(request, model_id):
    """delete a model in catalog after confirmation. If any model in production it will not be deleted until all lrelated models are not deleted"""
    model = get_object_or_404(Catalog, model_id=model_id)
    # get list of lots that model is in production and if it is not empty get message that model can not be deleted
    lot_ids = tuple(lot.lot_id.lot_id for lot in LotModels.objects.filter(model_id=model_id))
    if lot_ids:
        messages.error(request, f'მოდელი ვერ წაიშლება სანამ პარტია {lot_ids}-შია დამატებული!')
        return redirect('catalog')
    # if model is not in use delete it
    elif request.method == 'POST':
        model.delete()
        messages.success(request, 'მოდელი წარმატებით წაიშალა.')
        return redirect('catalog')

    return render(request, 'model_delete.html', {'model': model })


def model_stone_add(request, model_id):
    """add a new stone to model in catalog using dedicated form"""
    if request.method == 'POST':
        form = CatalogStonesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელზე ქვა წარმატებით დაემატა.')
            return redirect('catalog')
        else:
            messages.error(request, f'შეცდომა {form.errors} ქვის დამატებისას')
    else:
        form = CatalogStonesForm(initial={'model_id': model_id})

    return render(request, 'model_stone_add.html', {'form': form, 'model_id': model_id, 'action': 'დაამატე'})


def model_stone_delete(request, model_id, stone_full_name):
    """delete a model stone in catalog after confirmation. uses same template as lot model stone delete"""
    stone = get_object_or_404(CatalogStones, model_id=model_id, stone_full_name=stone_full_name)
    if request.method == 'POST':
        stone.delete()
        messages.success(request, 'მოდელზე ქვა წარმატებით წაშლილია.')
        return redirect('catalog')

    return render(request, 'stone_delete.html', {'stone': stone})


def model_2_lot_add(request, model_id, lot_id):
    """Will add model to lot from catalog or duplicate the existing lotmodel from lot_update.html"""
    login_db(request)
    # if model is duplicated from existing lotmodel from lot_update.html no need to create any forms, model_id is tmstmp
    # when lot-id is not null that indicates that function was called from lot form with duplicate button
    if lot_id != 0:
        data = pd_query(f"""SELECT lot_id, model_id, weight, cost_gram_gold, price_gram_gold FROM lot_models WHERE tmstmp = '{model_id}'""", POSTGRESQL_ENGINE)
        if data and insert_query('lot_models', [data[0].to_dict()], POSTGRESQL_ENGINE):
            messages.success(request, f"მოდელი {model_id} წარმატებით დაემატა პარტიაში {lot_id}.")
        else:
            messages.error(request, f"მოდელი {model_id} ვერ დაემატა პარტიაში {lot_id}.")
        return redirect('lot_update', lot_id=lot_id)

    # if it is created from catalog needed separate form to choose lot_id to witch adding
    form = LotListForm()
    image_location = get_object_or_404(Catalog, model_id=model_id).image_location
    if request.method == 'POST':
        data = [{"lot_id": request.POST.get('select_lot_id'), "model_id": model_id}, ]
        if insert_query('lot_models', data, POSTGRESQL_ENGINE):
            messages.success(request, f"მოდელი {model_id} წარმატებით დაემატა პარტიაში {request.POST.get('select_lot_id')}.")
        else:
            messages.error(request, f"მოდელი {model_id} ვერ დაემატა პარტიაში {request.POST.get('select_lot_id')}.")
        return redirect('catalog')

    return render(request, 'model_2_lot_add.html', {'form': form, 'model_id': model_id, 'image_location':image_location})


######################## lot ###########################


def lot_list(request):
    """list of lots and related info"""
    lots = Lots.objects.all()
    return render(request, 'lot_list.html', {'lots': lots})


def lot_create(request):
    """create a new lot"""
    if request.method == 'POST':
        form = LotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'პარტია წარმატებით დაემატა.')
            return redirect('lot_list')
    else:
        form = LotForm()
    return render(request, 'lot_form.html', {'form': form, 'action': 'შექმენი'})


def lot_update(request, lot_id):
    """contains a lot update form and same time shows a list of lot_models for the same lot with totals in the header"""

    login_db(request)
    # will get lot_model info from db view, not db table or django model.
    lot_models = pd_query(f'SELECT *, model_price - model_cost AS model_profit FROM lot_update_models WHERE lot_id = {lot_id}', POSTGRESQL_ENGINE)
    # add stone inforamtion as list of pandas series using sql query
    for lot_model in lot_models:
        # uses custom db view not db table or django model
        lot_model['lot_stones'] = pd_query(f"""SELECT * FROM lot_update_stones WHERE tmstmp = '{lot_model.tmstmp}'""", POSTGRESQL_ENGINE)

    # calculate totals for header
    lot_model_totals = pd.Series()
    lot_model_totals_temp = pd.DataFrame(lot_models)
    if not lot_model_totals_temp.empty:
        lot_model_totals['count'] = lot_model_totals_temp['model_id'].count()
        lot_model_totals['unique'] = len(lot_model_totals_temp['model_id'].unique())
        lot_model_totals['sold'] = len(lot_model_totals_temp[lot_model_totals_temp.location == 'გაყიდული'])
        lot_model_totals['weight'] = lot_model_totals_temp['weight'].sum()
        lot_model_totals['cost_gram_gold'] = lot_model_totals_temp['cost_gram_gold'].mean()
        lot_model_totals['price_gram_gold'] = lot_model_totals_temp['price_gram_gold'].mean()
        lot_model_totals['model_total_stone_weight'] = lot_model_totals_temp['model_total_stone_weight'].sum()
        lot_model_totals['model_total_stone_quantity'] = lot_model_totals_temp['model_total_stone_quantity'].sum()
        lot_model_totals['model_total_stone_cost_piece'] = lot_model_totals_temp['model_total_stone_cost_piece'].sum()
        lot_model_totals['model_total_stone_cost_manufacturing_stone'] = lot_model_totals_temp['model_total_stone_cost_manufacturing_stone'].sum()
        lot_model_totals['model_total_stone_margin_stones'] = lot_model_totals_temp['model_total_stone_margin_stones'].sum()
        lot_model_totals['model_cost'] = lot_model_totals_temp['model_cost'].sum()
        lot_model_totals['model_price'] = lot_model_totals_temp['model_price'].sum()
        lot_model_totals['model_profit'] = lot_model_totals['model_price'] - lot_model_totals['model_cost']

    # for lot info and update
    lot = get_object_or_404(Lots, lot_id=lot_id)
    if request.method == 'POST':
        form = LotForm(request.POST, instance=lot)
        if form.is_valid():
            form.save()
            messages.success(request, 'პარტიაზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('lot_update', lot_id=lot_id)
        else:
            messages.error(request, f'შეცდომა {form.errors} ინფორმაციის განახლებისას')
    else:
        form = LotForm(instance=lot)

    return render(request, 'lot_form.html', {'form': form, 'action': 'დაიმახსოვრე', 'lot_models':lot_models,
                                                                 'lot_model_totals':lot_model_totals})


def lot_delete(request, lot_id):
    """delete a lot after confirmation"""
    lot = get_object_or_404(Lots, lot_id=lot_id)
    if request.method == 'POST':
        lot.delete()
        messages.success(request, 'პარტია წარმატებით წაიშალა.')
        return redirect('lot_list')
    return render(request, 'lot_delete.html', {'lot': lot})


def lot_model_update(request, lot_id, model_id, tmstmp):
    """lot model update form. shows model price and cost including stones. gets information from django model"""
    # can be accessed from sevral pages so needs back information or default to lot update
    next_url = request.GET.get('next') or request.POST.get('next') or f'/lot/{lot_id}/update/'

    # customize form to hide not needed fields
    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)
    hidden_fields = ['lot_id', 'model_id', 'tmstmp']
    form = LotModelsForm(instance=lotmodel)
    for field in hidden_fields:
        form.fields[field].widget = HiddenInput()
        form.fields[field].label = ''

    if request.method == 'POST':
        form = LotModelsForm(request.POST, instance=lotmodel)
        if form.is_valid():
            form.save()
            messages.success(request, 'პარტიის მოდელზე ინფორმაცია წარმატებით განახლდა.')
            return redirect(next_url)
        else:
            messages.error(request, f'პრობლემა {form.errors} ინფორმაციის განახლებისას!')

    return render(request, 'lot_model_form.html', {'form': form, 'action': 'განახლება', 'next_url': next_url,
                                                                        'model_cost': lotmodel.model_cost, 'model_price': lotmodel.model_price,
                                                                        'model_profit': lotmodel.model_profit})


def lot_model_sold(request, lot_id, model_id, tmstmp):
    """for button sale that will use lot model update form with some fields hidden and pre-filled to tag model as sold"""
    # can be accessed from sevral pages so needs back information or default to lot update
    next_url = request.GET.get('next') or request.POST.get('next') or f'/lot/{lot_id}/update/'

    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)

    hidden_fields = ['lot_id', 'model_id']
    required_fields = ['customer', 'sale_date', 'price_gram_gold', 'location']
    initial = {'location': 'გაყიდული', 'sale_date': now()}
    form = LotModelsForm(instance=lotmodel, initial=initial)
    for field in hidden_fields:
        form.fields[field].widget = HiddenInput()
        form.fields[field].label = ''
    for field in required_fields:
        form.fields[field].widget.attrs.update({'required': True})

    if request.method == 'POST':
        form = LotModelsForm(request.POST, instance=lotmodel)
        if form.is_valid():
            form.save()
            messages.success(request, 'მოდელი გაიყიდა. არ დაგავიწყდეთ ფული აღების გატარება')
            return redirect(next_url)
        else:
            messages.error(request, 'პრობლემა მოდელის გაყიდვისას!')

    return render(request, 'lot_model_form.html', {'form': form, 'action': 'გაყიდვა', 'next_url': next_url,
                                                   'model_cost': lotmodel.model_cost,
                                                   'model_price': lotmodel.model_price,
                                                   'model_profit': lotmodel.model_profit})


def lot_model_return(request, lot_id, model_id, tmstmp):
    """form to fill when customer is returning sold model. Will create reverse transaction record for sold price if requested"""
    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)
    image_location = lotmodel.image_location
    full_name = lotmodel.customer
    price = lotmodel.model_price

    if request.method == 'POST':
        # will make reverse transaction for money that will be returned to customer if checkbox is selected
        if request.POST.get('return_money', 0):
            price = request.POST.get('price', 0)
            data = [{'transaction_type': 'გაყიდვა', 'item': 'ფული', 'item_type': 'შემოსავალი',
                     'description': f'მოდელი {model_id}-ს დაბრუნება', 'customer': full_name.full_name,
                     'transaction_quantity': -abs(float(price)),
                     'transaction_quantity_unit': 'ლარი', 'cost_unit': 1, }]
            login_db(request)
            insert_query('transactions', data, POSTGRESQL_ENGINE)
            messages.success(request, f'ავტომატურად ჩამოიჭრა {price} ლარი.')
        # will change location, custmer name and sale dates to not sold status
        lotmodel.location = ProductLocation.objects.get(label='სეიფი')
        lotmodel.customer = Customers.objects.get(full_name='NA')
        lotmodel.sale_date = None
        lotmodel.save()
        messages.success(request, f'მოდელი {model_id} დაბრუნა {lotmodel.location.label[:-1]}ში.')
        return redirect('customer_details', full_name=full_name)

    return render(request, 'lot_model_return.html', {'full_name': full_name, 'model_id':model_id,
                                                                         'image_location':image_location, 'price': price})


def lot_model_delete(request, lot_id, model_id, tmstmp):
    """will delete model from lot if it is not sold, giving note to first change sold value if it is sold"""
    lotmodel = get_object_or_404(LotModels, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp)

    # if it is sold give messsage to remove sold label and redirect to lot update
    if lotmodel.location.label == 'გაყიდული':
        messages.warning(request, f'მოდელი {model_id} მონიშნულია როგორც გაყიდული, წასაშლელად ჯერ გააუქმეთ მონიშვნა.')
        return redirect('lot_update', lot_id=lot_id)

    if request.method == 'POST':
        lotmodel.delete()
        messages.success(request, f'პარტია {lot_id}-ში მოდელი {model_id} წარმატებით წაშლილია.')
        return redirect('lot_update', lot_id=lot_id)

    return render(request, 'lot_model_delete.html',
                  {'lot_id': lot_id, 'model_id': model_id, 'image_location': lotmodel.image_location})


def lot_model_stone_add(request, lot_id, model_id, tmstmp):
    """add new stone to lot_model"""
    # get costs from lot default field to fill required filedს in lot_model_stone table
    cost_manufacturing_stone = django_sql(f"""(SELECT cost_manufacturing_stone FROM lots WHERE lot_id = {lot_id})""")[0][0] or 0
    margin_stones = django_sql(f"""(SELECT margin_stones FROM lots WHERE lot_id = {lot_id})""")[0][0] or 0
    initial = {'cost_manufacturing_stone': cost_manufacturing_stone, 'margin_stones': margin_stones}
    lot_model_stone = LotModelStones(lot_id=Lots.objects.get(lot_id=lot_id), model_id=Catalog.objects.get(model_id=model_id),
                                     tmstmp=LotModels.objects.get(tmstmp=tmstmp) )
    form = LotModelStonesForm(instance=lot_model_stone, initial=initial)

    if request.method == 'POST':
        form = LotModelStonesForm(request.POST, instance=lot_model_stone, initial=initial)
        if form.is_valid():
            form.save()
            messages.success(request, f"N {lot_id} პარტიაში {model_id} მოდელზე მოდელზე ქვა {request.POST.get('stone_full_name')} წარმატებით დაემატა.")
        else:
            messages.error(request, f'შეცდომა {form.errors} ქვის დამატებისას')
        return redirect('lot_update', lot_id=lot_id )

    return render(request, 'lot_model_stone_form.html', {'form': form, 'action': 'დამატება', 'lot_id':lot_id}, )


def lot_model_stone_change(request, lot_id, model_id, tmstmp, stone_full_name):
    "update lot_model_stone details using sql query"
    lot_model_stone = get_object_or_404(LotModelStones, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp, stone_full_name=stone_full_name)
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        # django requires its model and will not update field if it is key value, so using sql herein case stone_full_name update needed
        login_db(request)
        stat = f"""UPDATE lot_model_stones
                    SET stone_full_name = '{request.POST.get("stone_full_name")}',
                    quantity = {request.POST.get('quantity')},
                    cost_piece = {request.POST.get('cost_piece', 'NULL')},
                    cost_manufacturing_stone = {request.POST.get('cost_manufacturing_stone', 'NULL')},
                    margin_stones = {request.POST.get('margin_stones', 'NULL')},
                    installed = {request.POST.get('installed', False) },
                    note = '{request.POST.get("note", "NULL")}'
                   WHERE  lot_id={lot_id} AND model_id='{model_id}' AND tmstmp='{tmstmp}' AND stone_full_name='{stone_full_name}'"""
        try:
            crt_query(stat, POSTGRESQL_ENGINE)
        except Exception as e:
            messages.error(request, f'შეცდომა {e} ქვის შეცვლისას')
        else:
            messages.success(request, f"N { lot_id } პარტიაში { model_id } მოდელზე მოდელზე ქვა {stone_full_name} შეიცვალა {request.POST.get('stone_full_name')} ქვით")
        return redirect('lot_update', lot_id=lot_id )

    return render(request, 'lot_model_stone_form.html', {'form': form, 'action': 'შეცვლა'}, )


def lot_model_stone_delete(request, lot_id, model_id, tmstmp, stone_full_name):
    "delete stone after confirmation. uses same template as catalog_stone delete"
    stone = get_object_or_404(LotModelStones, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp, stone_full_name=stone_full_name)
    if request.method == 'POST':
        stone.delete()
        messages.success(request, f'პარტია {lot_id}-ში მოდელ {model_id}-ზე წაიშალა {stone_full_name} !')
        return redirect('lot_update', lot_id=lot_id)

    return render(request, 'stone_delete.html', {'stone': stone})


def lot_model_cost_default_update(request, lot_id, model_id, tmstmp, field):
    """Using SQL query to update lot_models cost_gram_gold and price_gram_gold fields with default value"""
    login_db(request)
    # default message is success
    message = 'ოპერაცია წარმატებით დასრულდა'

    # generate where clause for query. 'all' will be translated to field filter absence that will update all fields
    where = f""" WHERE {field} IS NULL AND lot_id = {lot_id} """
    where += "" if model_id == 'all' else f""" AND model_id = '{model_id}' """
    where += "" if tmstmp == 'all' else f""" AND tmstmp = '{tmstmp}' """

    # generate query based on field variable
    if field == 'cost_gram_gold':
        # if there is value in cost_calculation_per_lot view's cost_per_gram field for lot
        cost_gram_gold = django_sql(f"""SELECT cost_per_gram FROM cost_calculation_per_lot WHERE lot_id = {lot_id}""")[0][0]
        if cost_gram_gold:
            stat =f"""UPDATE lot_models SET cost_gram_gold = {cost_gram_gold} {where} """
            crt_query(stat, POSTGRESQL_ENGINE)
        else:
            message = 'ოქროს თვითღირებულება არ არის დაანგარიშებული'
    elif field == 'price_gram_gold':
        stat =f"""UPDATE lot_models SET price_gram_gold = (SELECT price_gram_gold FROM lots WHERE lot_id = {lot_id}) {where}"""
        crt_query(stat, POSTGRESQL_ENGINE)

    messages.success(request, message)
    # redirect to next or lot_updates
    next_url = request.GET.get('next', f'/lot/{lot_id}/update/')
    return redirect(next_url)


def lot_model_stone_default_update(request, lot_id, model_id, tmstmp, stone_full_name, field):
    """Using SQL query to update lot_model_stones cost_piece, cost_manufacturing_stone, margin_stones field with default value"""
    login_db(request)
    message = 'ოპერაცია წარმატებით დასრულდა'

    # generate where clause for query. 'all' will be translated to field filter absence that will update all fields
    where = f""" WHERE {field} IS NULL AND lot_id = {lot_id} """
    where += "" if model_id == 'all' else f""" AND model_id = '{model_id}' """
    where += "" if tmstmp == 'all' else f""" AND tmstmp = '{tmstmp}' """
    where += "" if stone_full_name == 'all' else f""" AND stone_full_name = '{stone_full_name}' """

    # remove total_ to match field name in db
    field = field.replace('total_', '')

    # generate query based on field variable
    if field in ['total_cost_piece', 'cost_piece']:
        # if there is stone purchase for last 6 month update price else change message content
        cost_piece = django_sql(f"""SELECT MAX( cost_piece ) FROM transactions 
                                        WHERE tmstmp > to_char(CURRENT_TIMESTAMP - '6 months'::INTERVAL, 'YY-MM-DD-HH24-MI-SS')
                                        AND item = '{stone_full_name}' GROUP BY item LIMIT 1""")
        if cost_piece:
            stat =f"""UPDATE lot_model_stones SET cost_piece = {cost_piece[0][0]} {where} """
            crt_query(stat, POSTGRESQL_ENGINE)
        else:
            message = f'{stone_full_name} არ არის ნაყიდი'
    elif field in ('cost_manufacturing_stone', 'margin_stones', 'total_cost_manufacturing_stone'):
        stat =f"""UPDATE lot_model_stones SET {field} = (SELECT {field} FROM lots WHERE lot_id = {lot_id} LIMIT 1) {where}"""
        crt_query(stat, POSTGRESQL_ENGINE)

    messages.success(request, message)
    # redirect to next or stone_totals
    next_url = request.GET.get('next', f'/lot/{lot_id}/stone_totals/')
    return redirect(next_url)


def lot_stone_totals(request, lot_id=0):
    """shows various tables for stones in lot. also provides labeling to link and update missing values and take out stones from stock and write to lot"""
    login_db(request)
    next_url = request.GET.get('next') or f'/lot/{lot_id}/update/'


    summary_tables = []
    # if lot_id is zero show all lot ids
    where_clause = f'lot_id = {lot_id}' if lot_id > 0 else f"lot_id > 0"
    # first table for required stones in lot grouped by stone name. gets data from custom db view
    header = 'პარტიაში დასამზადებელ (აუწონავ) მოდელებზე ქვების დაჯამებული სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'stone_full_name': 'ქვა', 'quantity': 'საჭირო რაოდ.', 'pieces': 'საწყობში',
                         'total_weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'transaction_quantity': 'საწყობში წონა', 'transaction_quantity_unit': 'ერთ.',
                         'total_cost_piece': 'ქვების ღირ.', 'avg_cost_piece': '1ც. საშ. ფასი', 'total_cost_manufacturing_stone': 'ჩასმის ღირ.',
                         'total_cost': 'სულ თვითღირ.', 'total_margin_stones': 'მოგება', 'total_price': 'ქვების გასაყ ფასი', 'action': '...' })]
    stat = f"""SELECT *, 'ჩამოწ.' FROM lot_stone_validation_totals WHERE {where_clause} ORDER BY err DESC, lot_id DESC, stone_full_name"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # first table for all stones in lot grouped by stone name. gets data from custom db view
    header = 'პარტიაში სულ ქვების დაჯამებული სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'stone_full_name': 'ქვა', 'quantity': 'საჭირო რაოდ.', 'pieces': 'საწყობში',
                         'total_weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'transaction_quantity': 'საწყობში წონა', 'transaction_quantity_unit': 'ერთ.',
                         'total_cost_piece': 'ქვების ღირ.', 'avg_cost_piece': '1ც. საშ. ფასი', 'total_cost_manufacturing_stone': 'ჩასმის ღირ.',
                         'total_cost': 'სულ თვითღირ.', 'total_margin_stones': 'მოგება', 'total_price': 'ქვების გასაყ ფასი', })]
    stat = f"""SELECT * FROM lot_stone_totals WHERE {where_clause} ORDER BY err DESC, lot_id DESC, stone_full_name"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # third table for all stones in lot grouped by stone name and model. gets data from db table
    header = 'პარტიაში, მოდელების მოხედვით სულ ქვების დაუჯამებელი სია'
    table = [pd.Series({'err': '!!!', 'lot_id': 'პარტ.', 'model_id': 'მოდელი', 'stone_full_name': 'ქვა', 'quantity': 'რაოდ.',
                         'weight': 'საჭირო წონა', 'weight_unit': 'ერთ.', 'cost_piece': 'ქვების ღირ.',
                         'cost_manufacturing_stone': 'ჩასმის ღირ.', 'total_cost': 'სულ თვითღირ.', 'margin_stones': 'მოგება', 'price': 'ქვების გასაყ ფასი', })]
    stat = f"""SELECT '' AS err, lot_id, model_id, stone_full_name, SUM(quantity), SUM(total_weight), weight_unit, SUM(total_cost_piece), 
                    SUM(total_cost_manufacturing_stone), SUM(total_cost), SUM(total_margin_stones), SUM(total_price)
               FROM lot_model_stones WHERE {where_clause} GROUP BY lot_id , model_id , stone_full_name, weight_unit ORDER BY lot_id DESC , model_id , stone_full_name;"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})

    return render(request, 'lot_stone_totals.html',{'summary_tables': summary_tables, 'next_url': next_url })


def lot_stone_withdrawal(request, stone_full_name, quantity, total_weight, weight_unit, total_cost_piece, lot_id ):
    """will create record in transactions table to take out stones from stock and also change status of those stones to installed"""
    login_db(request)
    # text that will desplayed as a working message
    message = f'N {lot_id} პარტიისთვის საწყობიდან {quantity} ცალი, {total_weight} {weight_unit} {stone_full_name} ქვის ჩამოწერა. ' +\
           f'საერთო ღირებულება: {total_cost_piece} ლარი . საშუალო ქვის ფასი: {round(float(total_cost_piece) / float(quantity),2)} ლარი. ' + \
           'გადაამოწმე თუ ემთხვევა ქვემოთ მოცემულ საწყობის მონაცემებს!'
    # table for remaining stones in stock from custom db view that are grouped by item (name) and quantity_unit
    header = 'ქვების მარაგები'
    table = [pd.Series({'stone_full_name': 'ქვები ჯამურად', 'transaction_quantity': 'რაოდენობა', 'transaction_quantity_unit': 'ერთეული',
                        'pieces': 'ცალობა', 'total_price': 'სულ ფასი', 'average_price_piece': 'ცალის ფასი'})]
    stat = f"""SELECT * FROM total_stones_stock WHERE stone_full_name = '{stone_full_name}'"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    stone_table = {header: table}

    if request.method == 'POST':
        # create transaction record and insert to db using sql
        data = [{'lot_id': lot_id, 'transaction_type': 'დამუშავება', 'item': stone_full_name,
                 'item_type': 'ქვა', 'description': 'საწყობიდან აღება',
                 'transaction_quantity': -abs(float(total_weight)), 'pieces': -abs(int(quantity)),
                 'transaction_quantity_unit': weight_unit, 'cost_unit': round(float(total_cost_piece) / float(total_weight), 2) }]
        try:
            insert_query('transactions', data, POSTGRESQL_ENGINE)
        except Exception as e:
            messages.error(request, f'პრობლემა {e} საწყობიდან ქვების აღების გატარებისას.')
        else:
            messages.success(request, f'საწყობიდან ქვების აღების გატარება წარმატებით დასრულდა.')

        # change status of related stones to installed
        stat = f"""UPDATE lot_model_stones SET installed = true WHERE stone_full_name = '{stone_full_name}' AND lot_id = {lot_id}"""
        try:
            crt_query(stat, POSTGRESQL_ENGINE)
        except Exception as e:
            messages.error(request, f'პრობლემა {e} ქვების დაყენების სტატუსის მიცემისას.')
        else:
            messages.success(request, f'ქვებს წარმატებით მიეცათ სტატუსი დაყენებული.')

        return redirect('lot_stone_totals', lot_id )

    return render(request, 'lot_stone_withdrawal.html', {'stone_table': stone_table, 'lot_id': lot_id, 'message': message})


######################## customers #############################


def customer_list(request):
    """list of cutomers and related information from custom db view"""
    login_db(request)
    customers = pd_query('SELECT * FROM customer_details;', POSTGRESQL_ENGINE)
    return render(request, 'customer_list.html', {'customers': customers})


def customer_create(request):
    """create a new customer with related information"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'მომხმარებელი წარმატებით დაემატა.')
            return redirect('customer_list')
        else:
            messages.error(request, f'შეცდომა {form.errors} ქვის დამატებისას')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form, 'action': 'დაამატე'})


def customer_details(request, full_name):
    """provides/updates information about customer info and table of customer-owned models"""
    # customer instance to create form later
    customer = get_object_or_404(Customers, full_name=full_name)
    # create locations instance that includes all locations that indicates customer ownership on product, bought or not bought
    locations = ProductLocation.objects.filter(label__in=['დახლი', 'გაყიდული'])
    # filter lot_models with customer name and customer location created above. it will be used as table of models that owns customer
    purchases = LotModels.objects.filter(customer=full_name, location__in=locations).order_by('-sale_date','-lot_id', '-model_id')
    form = CustomerForm(instance=customer)

    # form also updates customer details
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            # if there is name change use sql to change customer name and after save using django form.save
            if request.POST.get('full_name', '') != full_name:
                login_db(request)
                stat = f"""UPDATE customers SET full_name = '{form.instance.full_name}' WHERE full_name = '{full_name}'"""
                try:
                    crt_query(stat, POSTGRESQL_ENGINE)
                except Exception as e:
                    messages.error(request, f'პრობლემა {e} მომხმარებლს სახელის განახლებისას!')
                else:
                    messages.success(request, 'მომხმარებლის სახელი წარმატებით განახლდა.')
            form.save()
            messages.success(request, 'მომხმარებელზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('customer_list')

    return render(request, 'customer_form.html', {'form': form, 'action': 'დაიმახსოვრე', 'purchases': purchases})


def customer_delete(request, full_name):
    """deletes customer if he/she does not own any models or have any transactions"""
    customer = get_object_or_404(Customers, full_name=full_name)
    if request.method == 'POST':
        # check if customer have any models owned and records in transactions
        if customer.count_models_owned or customer.count_transactions:
            messages.error(request,
                  f'ვერ მოხდება მომხმარებლის წაშლა რადგან აქვს {customer.count_models_owned} მოდელი და {customer.count_transactions} გატარება')
            return redirect('customer_list')
        customer.delete()
        messages.success(request, 'მომხმარებელი წარმატებით წაიშალა.')
        return redirect('customer_list')
    return render(request, 'customer_delete.html', {'customer': customer})


######################## transactions ###########################


def transaction_list(request, transaction_type = 'ნებისმიერი', order_by='-tmstmp:transaction_type:lot_id:item'):
    """list of transactions with totals in heading and filter"""
    login_db(request)
    # TODO: implement pagination and sorting later
    # create sql order by statement
    order_by = [f"{field.replace('-', '')}  DESC" if '-' in field else field for field in order_by.split(':')]
    order_by = 'ORDER BY ' + ' , '.join(order_by)

    # create sql where clause based on transaction_type argument
    if transaction_type == 'ნებისმიერი':
        where = 'true'
    elif transaction_type == 'პარტია':
        where = f"lot_id > 0"
    else:
        where = f"transaction_type = '{transaction_type}'"
    where = 'WHERE ' + where

    # create transactions table
    stat = f"""SELECT * FROM transactions {where} {order_by}"""
    transactions = pd_query(stat, POSTGRESQL_ENGINE)

    # form for filter
    form = AddTransactionForm(request.POST)
    # remove required tags for filter fields
    form.use_required_attribute = False
    # if there is post and transactions is not empty
    if request.method == 'POST' and len(transactions):
        # take first record and get index for fields
        fields = transactions[0].index
        for key, value in request.POST.items():
            # if value is not empty and key is for filter fields. filter is additive
            if value != '' and key in fields or key in ['from', 'to']:
                # this part is for numeric that is only lot_id at this moment
                if isinstance(value, (int, float)):
                    where += f" AND {key} = {value}"
                # from date and to date filters, using first part of tmstmp that is date part
                elif key == 'from_date' and value:
                    where += f" AND tmstmp > '{value[-8:]}-00-00-00'"
                elif key == 'to_date' and value:
                    where += f" AND tmstmp < '{value[-8:]}-99-99-99'"
                # for description part uses like not exact equal
                elif key == 'description' and value:
                    where += f" AND  {key} ILIKE '%{value}%'"
                # for others using strict equal
                elif key not in ['from_date', 'to_date']:
                    where += f" AND {key} = '{value}'"
        # recreate transactions table
        stat = f"""SELECT * FROM transactions {where} {order_by}"""
        transactions = pd_query(stat, POSTGRESQL_ENGINE)
    # create totals dataframe
    totals = pd.DataFrame(transactions)
    for transaction in transactions:
        # extract date from tmstmp
        transaction['date'] = transaction['tmstmp'][:8]

    return render(request, 'transaction_list.html', {'transactions': transactions, 'form': form,
                                                                         'totals': totals, 'transaction_type':transaction_type})


def transaction_create(request, transaction_identifier='ნებისმიერი', lot_id=0):
    """creates record in transactions table, based on transaction_identifier and lot_id will auto fill form and provide various informational tables"""
    ############create tables##################
    ###########################################
    login_db(request)
    # list of lot's transactions
    header = 'პარტიაზე გატარებების სია (მაქს. 30)'
    table = [pd.Series(
        {'lot_id': 'პრტ.N', 'description': 'იდენტიფიკატორი', 'tmstmp': 'თარიღი', 'transaction_type': 'ტრნზ.ტიპი',
         'item': 'მსლ./მომსხ.', 'item_type': 'მასალის ტიპი', 'transaction_quantity': 'რაოდენობა',
         'cost_unit': 'ერთ. ფასი',
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
    table = [pd.Series({'item': 'მეტალები ჯამურად', 'total_quantity': 'სულ (გრამი)', 'cost_unit': 'ერთეულის ფასი',
                        'total_cost': 'სულ ფასი'})]
    stat = """SELECT * \
              FROM total_metals_per_metal"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    materials_tables.append({header: table})
    header = 'სხვა მასალების სია'
    table = [pd.Series({'item': 'სხვა მატერიალები ჯამურად', 'total_quantity': 'სულ', 'cost_unit': 'ერთეულის ფასი',
                        'total_cost': 'სულ ფასი'})]
    stat = """SELECT * \
              FROM total_other_materials"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    materials_tables.append({header: table})

    # summary tables
    summary_tables = []
    header = 'გადაყვანები'
    table = [pd.Series({'transaction_date': 'ბოლო 5 თარიღზე გადაყვანები', 'total_weight_in': 'სულ გადასაყვანად (გრამი)',
                        'total_weight_out': 'სულ გადაყვანილი (გრამი)', 'total_weight_lost': 'დანაკარგი (გრამი)',
                        'total_cost_in': 'სულ გადასაყვანად (ლარი)', 'cost_per_gram': 'გრამის ღირებულება'})]
    stat = """SELECT * \
              FROM total_sinji_per_date \
              LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # summary table for cast and processing
    header = 'ჩამოსხმები'
    table = [pd.Series({'lot_id': 'ბოლო 5 პარტიაზე ჩამოსხმები', 'total_weight_in': 'სულ ჩამოსასხმელად (გრამი)',
                        'total_weight_out': 'სულ ჩამოსხმული (გრამი)',
                        'total_weight_lost': 'ჩამოსხმის დანაკარგი (გრამი)',
                        'total_cost_lost': 'ჩამოსხმის დანაკარგი (ლარი)',
                        'total_cost': 'ჩამოსხმის ღირებულება', 'total_salary': 'აქედან ხელფასი'})]
    stat = """SELECT * \
              FROM total_cast_per_lot \
              LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    header = 'დამუშავებები'
    table = [pd.Series({'lot_id': 'ბოლო 5 პარტიაზე დამუშავება', 'total_weight_in': 'სულ დასამუშავებელი (გრამი)',
                        'total_weight_out': 'სულ დამუშავებული (გრამი)', 'total_cost_out': 'სულ დამუშავებული (ლარი)',
                        'total_weight_lost': 'დამუშავების დანაკარგი (გრამი)',
                        'total_cost_lost': 'დამუშავების დანაკარგი (ლარი)',
                        'total_cost': 'დამუშავების ღირებულება', 'total_salary': 'აქედან ხელფასი'})]
    stat = """SELECT * \
              FROM total_processing_per_lot \
              LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # lot models totals table
    header = 'პარტიის მოდელებზე მონაცემები'
    table = [
        pd.Series({'lot_id': 'ბოლო 5 პარტაზე მოდელების ჯამები', 'total_weight_models': 'სულ წონა ბეჭდებიდან (გრამი)',
                   'model_count': 'მოდელების რაოდენობა (ცალი)', 'pieces_sum': 'ნაჭრების ჯამი'})]
    stat = """SELECT * \
              FROM total_lot_model_per_lot \
              LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    summary_tables.append({header: table})
    # salary table
    header = 'ხელფასები'
    table = [pd.Series({'lot_id': 'ბოლო 5 პარტაზე ხელფასები', 'cost_casting': 'ჩამოსხმა', 'cost_grinding': 'დამუშავება',
                        'cost_manufacturing_stone': 'თვლის ჩასმა', 'cost_polishing': 'გაპრიალება',
                        'cost_plating': 'როდირება', 'cost_sinji': 'სინჯი', 'total_salary': 'სულ'})]
    stat = """SELECT * \
              FROM salaries_per_lot \
              LIMIT 5"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    # delete total_salary field as it is not totals for all fields but is used for auto-salary calculations
    [item.drop('total_salary', inplace=True) for item in table]
    summary_tables.append({header: table})
    # gold cost calculation
    header = 'საბოლოო ჯამები'
    table = [pd.Series({'lot_id': 'ბოლო 5 პარტია', 'total_weight_out': 'დამუშავებული ოქროს წონა (გრამი)',
                        'total_cost_out': 'დამუშავებული ოქროს ფასი',
                        'total_weight_lost': 'სულ დანაკარგი (გრამი)', 'total_cost_lost': 'სულ დანაკარგი (ლარი)',
                        'total_salary_other_cost': 'ხელფასები და სხვა', 'total_cost': 'სულ ოქროს თვითღირებულება',
                        'cost_per_gram': 'გრამის თვითღირებულება', 'total_lot_cost': 'პარტიის თვითღირებულება'})]
    stat = """SELECT * \
              FROM cost_calculation_per_lot \
              LIMIT 5"""
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
        # custom choise field for gold lost during production
        metal_lost = [[f'{metal_full_name} დანაკარგი', f'{metal_full_name} დანაკარგი']]
    else:
        initial = {}
        hidden_fields = []
        metals = [['', '---მეტალები---']] + sorted([([o.metal_full_name] * 2) for o in Metals.objects.all()])
    stones = [['', '---ქვები---']] + sorted([([o.stone_full_name] * 2) for o in Stones.objects.all()])
    other_items = [['', '---სხვა---']] + sorted([([o.label] * 2) for o in Assets.objects.all()])

    # from which page it was transfered used to crete description field.
    # there are several similar sub transaction types  that can be linked to different transaction types
    if 'დამუშავება' in request.GET.get('next', ''):
        transaction_type = 'დამუშავება'
    elif 'ჩამოსხმა' in request.GET.get('next', ''):
        transaction_type = 'ჩამოსხმა'
    elif 'გადაყვანა' in request.GET.get('next', ''):
        transaction_type = 'გადაყვანა'
    else:
        transaction_type = 'ნებისმიერი'
    danshi = 'იდან' if 'აღება' in transaction_identifier else 'ში'

    # based on transaction_identifier crete form with initial, item_choices and hidden fields
    match transaction_identifier:
        case 'გადაყვანა':
            initial.update({'transaction_type': transaction_identifier, 'item_type': 'მეტალი',
                            'transaction_quantity_unit': 'გრამი'})
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location', 'customer'])
        case 'ქვის_შესყიდვა':
            transaction_type = 'შესყიდვა'
            initial.update({'transaction_type': transaction_type, 'item_type': 'ქვა', })
            item_choices = stones
            item_label = 'აირჩიე ქვა'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'customer'])
        case 'მეტალის_შესყიდვა':
            transaction_type = 'შესყიდვა'
            initial.update(
                {'transaction_type': transaction_type, 'item_type': 'მეტალი', 'transaction_quantity_unit': 'გრამი'})
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location', 'customer'])
        case 'გაყიდვა':
            transaction_type = 'გაყიდვა'
            initial.update({'transaction_type': transaction_type, 'item': 'ფული', 'item_type': 'შემოსავალი',
                            'transaction_quantity_unit': 'ლარი', 'cost_unit': 1, })
            item_choices = other_items + metals + stones
            item_label = 'ფული'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location', ])
        case 'ჩამოსხმა' | 'დამუშავება':
            initial.update({'lot_id': lot_id, 'transaction_type': transaction_identifier})
            item_choices = metals + metal_lost + other_items
            item_label = 'აირჩიე მეტალი/მეტალის დანაკარგი/ფული'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location', 'customer'])
        case 'მეტალის_აღება' | 'მეტალის_დაბრუნება':
            if lot_id:
                initial.update({'lot_id': lot_id, 'transaction_type': transaction_type,
                                'item': metal_full_name, 'item_type': 'მეტალი',
                                'transaction_quantity_unit': 'გრამი',
                                'description': f"""{transaction_identifier.split('_')[1]} საწყობ{danshi}"""})
                item_choices = metals
                item_label = 'აირჩიე მეტალი'
                hidden_fields.extend(initial.keys())
                hidden_fields.extend(['pieces', 'stone_quality', 'image_location', 'customer'])
            else:
                initial.update(
                    {'transaction_type': transaction_type, 'item_type': 'მეტალი', 'transaction_quantity_unit': 'გრამი',
                     'description': f"""{transaction_identifier.split('_')[1]} საწყობ{danshi}"""})
                item_choices = metals
                item_label = 'აირჩიე მეტალი'
                hidden_fields.extend(initial.keys())
                hidden_fields.extend(['lot_id', 'pieces', 'stone_quality', 'image_location', 'customer'])
        case 'მეტალის_დანაკარგი':
            initial.update({'lot_id': lot_id, 'transaction_type': transaction_type,
                            'item': f'{metal_full_name} დანაკარგი', 'item_type': 'მეტალი',
                            'transaction_quantity_unit': 'გრამი',
                            'description': 'დანაკარგი'})
            item_choices = metals
            item_label = 'აირჩიე მეტალი'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location', 'customer'])
        case 'ხელფასი':
            initial.update({'lot_id': lot_id, 'transaction_type': transaction_type, 'transaction_quantity_unit': 'ლარი',
                            'cost_unit': 1,
                            'item': 'ფული', 'item_type': 'მომსახურება', 'description': 'მომსახერება/ხელფასის გადახდა'})
            item_choices = other_items + metals + stones
            item_label = 'ფული'
            hidden_fields.extend(initial.keys())
            hidden_fields.extend(['pieces', 'stone_quality', 'image_location', 'customer'])
            # to remove field from hidden field
            hidden_fields.remove('description')
        case 'ინფორმაცია':
            item_choices = [['', '']]
            item_label = ''
            hidden_fields = list(AddTransactionForm().fields.keys())
        case _:
            item_choices = metals + other_items + stones
            item_label = 'აქტივი'

    # if transaction type is not in db and transaction field is autofilled above show transaction type field
    if transaction_type not in TransactionTypes.objects.all().values_list('label', flat=True) and hidden_fields.count(
            'transaction_type'):
        hidden_fields.remove('transaction_type')
    form = AddTransactionForm(initial=initial)
    form.fields['item'] = ChoiceField(choices=item_choices, widget=Select(attrs={'class': 'form-control'}),
                                      label=item_label)
    for field in hidden_fields:
        form.fields[field].widget = HiddenInput()
        form.fields[field].label = ''
    ###########################################
    ##############create form##################

    ##########create redirect logic############
    ###########################################
    # if lot_id is not 0 or None next redirect to lot update, else if transaction_type is not empty to list of transaction_type and if it is empty to all list
    if initial.get('transaction_type', None):
        redirect_url = f'/lot/{lot_id}/update/' if lot_id else f'/transaction_list/{transaction_type}/transaction_type/'
    else:
        redirect_url = f'/lot/{lot_id}/update/' if lot_id else f'/transaction_list/'
    next_url = request.GET.get('next') or request.POST.get('next')
    redirect_url += f'?next={next_url}'
    ###########################################
    ##########create redirect logic############

    if request.method == 'POST':

        form = AddTransactionForm(request.POST, request.FILES)
        if form.is_valid():
            # validate sign of quantity based on from or out of stock, it only works for metal and salary, other should control user
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
            return redirect(redirect_url)
        else:
            messages.error(request, f'შეცდომა: {form.errors}')

    return render(request, 'transaction_form.html',
                  {'form': form, 'transaction_identifier': transaction_identifier, 'action': 'დამატება',
                   'materials_tables': materials_tables, 'summary_tables': summary_tables,
                   'transactions_table': transactions_table, 'next_url': next_url, })


def transaction_delete(request, tmstmp, item):
    """will delete transaction record after confirmation"""
    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)
    # if lot_id is not null next url is lot update else all transaction list
    next_url = f'/lot/{transaction.lot_id}/update/' if transaction.lot_id else '/transaction_list/'
    next_url = request.GET.get('next') or request.POST.get('next') or next_url

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'ტრანზაქცია წარმატებით წაიშალა.')
        return redirect(next_url)
    return render(request, 'transaction_delete.html', {'transaction': transaction, 'next_url': next_url})


def transaction_update(request, tmstmp, item, transaction_identifier='ნებისმიერი'):
    """update transaction record"""
    transaction = get_object_or_404(Transactions, tmstmp=tmstmp, item=item)
    form = AddTransactionForm(instance=transaction)
    # if lot_id is not null next url is lot update else all transaction list
    next_url = '/transaction_list/' if transaction.lot_id == 0 else f'/lot_update/{transaction.lot_id}/update/'
    next_url = request.GET.get('next') or request.POST.get('next') or next_url

    if request.method == 'POST':
        form = AddTransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'ტრანზაქციაზე ინფორმაცია წარმატებით განახლდა.')
            return redirect(next_url)
        else:
            messages.error(request, f'პრობლემა {form.errors} ინფორმაციის განახლებისას!')

    return render(request, 'transaction_form.html', {'form': form, 'transaction_identifier': transaction_identifier,
                                                                         'action': 'შეცვლა', 'next_url': next_url})


def auto_salary(request, lot_id):

    ############create tables##################
    login_db(request)
    # table of already paid salary records
    header = 'პარტიაზე უკვე გადახდილი ხელფასები '
    table = [pd.Series({'lot_id': 'პრტ.N', 'description':'იდენტიფიკატორი', 'tmstmp': 'თარიღი', 'transaction_type': 'ტრნზ.ტიპი',
                         'item': 'მსლ./მომსხ.', 'item_type': 'მასალის ტიპი', 'transaction_quantity': 'რაოდენობა', 'cost_unit': 'ერთ. ფასი',
                         'total_cost': 'სულ ფასი', 'act': '...'})]
    stat = f"""SELECT * FROM records_for_summary WHERE lot_id = {lot_id} AND item_type = 'მომსახურება' ORDER BY lot_id DESC, tmstmp DESC LIMIT 30"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    transactions_tables = [{header: table}]
    # table of other gold processing records
    header = 'პარტიაზე დამუშავების სხვა გატარებები'
    table = [pd.Series({'lot_id': 'პრტ.N', 'description':'იდენტიფიკატორი', 'tmstmp': 'თარიღი', 'transaction_type': 'ტრნზ.ტიპი',
                         'item': 'მსლ./მომსხ.', 'item_type': 'მასალის ტიპი', 'transaction_quantity': 'რაოდენობა', 'cost_unit': 'ერთ. ფასი',
                         'total_cost': 'სულ ფასი', 'act': '...'})]
    stat = f"""SELECT * FROM records_for_summary WHERE lot_id = {lot_id} AND item_type != 'მომსახურება' ORDER BY lot_id DESC, tmstmp DESC LIMIT 30"""
    table.extend(pd_query(stat, POSTGRESQL_ENGINE))
    transactions_tables.append({header: table})

    # variables for calculation
    # total weight of gold that master took for processing
    total_weight_out = django_sql(f'SELECT total_weight_out FROM total_processing_per_lot WHERE lot_id = {lot_id}')[0][0]
    # metal name that is metal of lot
    metal_full_name = django_sql(f'SELECT metal_full_name FROM lots WHERE lot_id = {lot_id}')[0][0]
    # cost of 1 gram gold used for auto form filling calculated from earlier transaction records
    stat = f"""SELECT COALESCE(AVG(cost_unit), 0) AS cost_unit FROM transactions WHERE lot_id = {lot_id} and transaction_type = 'ჩამოსხმა' AND item_type = 'მეტალი'"""
    cost_unit = round(float(django_sql(stat)[0][0]), 2)
    # pd series of different type of salaries
    salaries = pd_query(f"""SELECT * FROM salaries_per_lot WHERE lot_id = '{lot_id}'""", POSTGRESQL_ENGINE)[0]
    # pd series of default prices for different types of master's services needed
    prices = pd_query(f"""SELECT * FROM lots WHERE lot_id = '{lot_id}'""", POSTGRESQL_ENGINE)[0]
    # units for auto-filling transaction form based on salary type
    units = {'cost_grinding': 'გრამი', 'cost_manufacturing_stone': 'ცალი', 'cost_polishing': 'ნაჭერი', 'cost_plating': 'ნაჭერი', 'cost_sinji': 'ნაჭერი'}
    # descriptions for auto-filling transaction form based on salary type
    descriptions = {'cost_grinding': 'დამუშავების', 'cost_manufacturing_stone': 'თვლის ჩასმის', 'cost_polishing': 'გაპრიალების',
                    'cost_plating': 'როდირების', 'cost_sinji': 'სინჯის'}

    if request.method == 'POST':
        # list of checkboxes that are checked
        salary_list = request.POST.getlist('salary_list')
        # if checkbox for getting gold from master is checked make appropriate auto transactions for lost gols and gold returned
        if request.POST.get('apply_gold_lost', None):
            data = [{'lot_id': lot_id, 'transaction_type': 'დამუშავება', 'item': metal_full_name, 'item_type': 'მეტალი',
                    'description': 'მოტანილი ნაქლიბი', 'transaction_quantity': abs(float(request.POST.get('remaining_gold'))),
                    'transaction_quantity_unit': 'გრამი', 'cost_unit': cost_unit, }]
            try:
                insert_query('transactions', data, POSTGRESQL_ENGINE)
            except Exception as e:
                messages.error(request, f'პრობლემა {e} მოტანილი მეტალის გატარების შესრულებისას!')
            else:
                messages.success(request, 'მოტანილი მეტალის გატარება წარმატებით შესრულდა.')
            data = [{'lot_id': lot_id, 'transaction_type': 'დამუშავება', 'item': f'{metal_full_name} დანაკარგი',
                     'item_type': 'მეტალი', 'description': 'დანაკარგი', 'transaction_quantity': abs(float(request.POST.get('lost_gold'))),
                     'transaction_quantity_unit': 'გრამი', 'cost_unit': cost_unit, }]
            try:
                insert_query('transactions', data, POSTGRESQL_ENGINE)
            except Exception as e:
                messages.error(request, f'პრობლემა {e} მეტალის დანაკარგის გატარების შესრულებისას!')
            else:
                messages.success(request, 'მეტალის დანაკარგის გატარება წარმატებით შესრულდა.')
        # create transaction records for each salary type that was checked using check boxes
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
                messages.error(request, f"""პრობლემა {e} {data[0]['description']} ხელფასების შეყვანისას.""")
            else:
                messages.success(request, f"""{data[0]['description']} გატარება წარმატებით გატარდა.""")
        return redirect('auto_salary', lot_id)

    return render(request, 'auto_salary.html', {'transactions_tables': transactions_tables, 'lot_id' : lot_id, 'salaries': salaries,
                                                                     'total_weight_out': total_weight_out, })


######################## other ###########################


def lookup_table(request, table_name, action, label):
    """using custom form instead of django admin to add/change info on lookup tables"""
    next_url = request.GET.get('next') or request.POST.get('next')
    lookup_table_dict = {'units': ['ერთეულები', Units], 'stone_names': ['ქვის სახელები', StoneNames], 'stone_qualities': ['ქვის ხარისხი', StoneQualities],
                         'genders': ['სქესი', Genders], 'model_categories': ['მოდელის კატეგორია', ModelCategories], 'masters': ['ხელოსნები', Masters],
                         'transaction_types': ['ტრანზაქციის ტიპები', TransactionTypes], 'item_types': ['აქტივის ტიპი/დანიშნულება', ItemTypes],
                         'assets': ['სხვა აქტივები', Assets], 'product_location': ['პროდუქტის მდებარეობა', ProductLocation],
                         'metals': ['მეტალები', Metals, MetalsForm], 'stones': ['ქვები', Stones, StonesForm], }
    ############create tables##################
    login_db(request)
    table = pd_query(f"""SELECT * FROM {table_name} ORDER BY 1, 2""", POSTGRESQL_ENGINE)
    header = f'დამხმარე სია: {lookup_table_dict[table_name][0]}'
    ##############create form and get model##################
    # create class form using model in dictionary above, initialize later.
    if table_name == 'metals':
        table = pd.DataFrame(table)
        table.insert(0, 'label', table['metal_full_name'])
        table.drop(columns=['metal_full_name', 'django_id'], inplace=True)
        table = [row for _, row in table.iterrows()]
        LookupForm = lookup_table_dict[table_name][2]
        lookup_model = lookup_table_dict[table_name][1].objects.filter(metal_full_name=label).first()
    elif table_name == 'stones':
        table = pd.DataFrame(table)
        table.insert(0, 'label', table['stone_full_name'])
        table.drop(columns=['stone_full_name', 'django_id'], inplace=True)
        table = [row for _, row in table.iterrows()]
        LookupForm = lookup_table_dict[table_name][2]
        lookup_model = lookup_table_dict[table_name][1].objects.filter(stone_full_name=label).first()
    else:
        # all simple lookup tables have same structure and created here as it can not be created in forms.py with different models
        LookupForm = modelform_factory(
            lookup_table_dict[table_name][1],
            fields=['label', 'note'],
            widgets={'label': TextInput(attrs={'class': 'form-control' }),
                     'note': Textarea(attrs={'class': 'form-control', 'rows': 3 }), },
            labels={'label': 'დასახელება',
                    'note': 'კომენტარი', } )
        lookup_model = lookup_table_dict[table_name][1].objects.filter(label=label).first()

    # initialize form
    form = LookupForm(instance=lookup_model)

    # delete action will try to delete lookup_model with appropriate messages
    if action == 'წაშლა' and lookup_model:
        try:
            lookup_model.delete()
        except Exception as e:
            messages.error(request, f'პრობლემა {e} {lookup_model}-ის წაშლისას, სავარაუდოდ გამოყენებულია სისტემაში!')
        else:
            messages.success(request, f'{label} წაშლილია.')
        next_url = reverse('lookup_table', kwargs={'table_name':table_name, 'action':action, 'label':' '}) + f'?next={next_url}'
        return redirect(next_url)

    # for creation and update of lookup table
    if request.method == 'POST':
        form = LookupForm(request.POST, instance=lookup_model)
        if form.is_valid():
            form.save()
            messages.success(request, f'{form.instance} წარმატებით დაემატა/შეიცვალა.')
            next_url = reverse('lookup_table', kwargs={'table_name': table_name, 'action': action, 'label': ' '}) + f'?next={next_url}'
            return redirect(next_url)
        else:
            messages.error(request, f'შეცდომა: {form.errors}')

    return render(request, 'lookup_table.html', {'form': form, 'table': table, 'table_name': table_name,
                                                                     'header': header, 'next_url': next_url})


################## in progress views ######################

def home(request):
    # login to db in any view that uses pandas
    return render(request, 'home.html')


# TODO: ideas to add
# add database users