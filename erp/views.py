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
                s.weight * cs.quantity::integer AS total_weight,
                s.weight, cs.quantity,
                CONCAT(cs.quantity::integer::text, ' ', cs.quantity_unit) AS quantity_unit
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
    if model_id in LotModels.objects.values_list('model_id', flat=True):
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
    lots = Lots.objects.all()
    # stat = """SELECT l.lot_id, l.lot_date, l.metal_full_name, l.master_full_name, l.note,
    #             lot.model_quantity, lot.price, lot.cost
    #           FROM lots AS l
    #             LEFT JOIN production_models AS pm ON l.lot_id = pm.lot_id"""
    # catalog_stones = pd_query(stat, POSTGRESQL_ENGINE)
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


from .models import LotModels
def lot_update(request, lot_id):
    login_db(request)
    lot = get_object_or_404(Lots, lot_id=lot_id)

    stat = f"""SELECT c.image_location, lm.model_id, lm.tmstmp
               FROM lot_models AS lm
                LEFT JOIN catalog AS c ON lm.model_id = c.model_id
               WHERE lm.lot_id = {lot_id}"""
    lot_models = pd_query(stat, POSTGRESQL_ENGINE)

    stat = f"""SELECT lms.model_id, lms.stone_full_name, lms.quantity, lms.weight, lms.tmstmp,
                    lms.quantity * lms.weight AS total_weight
               FROM lot_model_stones AS lms
               WHERE lms.lot_id = {lot_id}"""
    lot_stones = pd_query(stat, POSTGRESQL_ENGINE)

    # lotmodels = LotModels.objects.filter(lot_id=lot_id)
    # lotmodels = get_list_or_404(LotModels, lot_id=lot_id)
    # for each in lotmodels:
    #     model = get_object_or_404(Catalog, model_id=each.model_id)
    #     image = model.image_location
    #     each.__setattr__('image', image)
    #     print(each.image)

    if request.method == 'POST':
        lotform = LotForm(request.POST, instance=lot)
        if lotform.is_valid():
            lotform.save()
            messages.success(request, 'პარტიაზე ინფორმაცია წარმატებით განახლდა.')
            return redirect('lot_list')
    else:
        lotform = LotForm(instance=lot)

    return render(request, 'lot_form.html', {'lotform': lotform, 'action': 'შეცვალე', 'lot_models':lot_models, 'lot_stones':lot_stones})

    all_models = Catalog.objects.all()
    stat = """SELECT cs.model_id, cs.stone_full_name, 
                s.weight * cs.quantity::integer AS total_weight,
                s.weight, cs.quantity,
                CONCAT(cs.quantity::integer::text, ' ', cs.quantity_unit) AS quantity_unit
              FROM catalog AS c
                LEFT JOIN catalog_stones AS cs ON c.model_id = cs.model_id
                LEFT JOIN stones AS s on cs.stone_full_name = s.stone_full_name"""
    all_model_stones = pd_query(stat, POSTGRESQL_ENGINE)
    return render(request, 'model_list.html', {'all_models': all_models, 'all_model_stones': all_model_stones})


def lot_delete(request, lot_id):
    lot = get_object_or_404(Lots, lot_id=lot_id)
    if request.method == 'POST':
        lot.delete()
        messages.success(request, 'პარტია წარმატებით წაიშალა.')
        return redirect('lot_list')
    return render(request, 'lot_delete.html', {'lot': lot})


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

    lot_model_stone = LotModelStones(
        lot_id=Lots.objects.get(lot_id=lot_id),
        model_id=Catalog.objects.get(model_id=model_id),
        tmstmp=LotModels.objects.get(tmstmp=tmstmp),
    )
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        form = LotModelStonesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"N { lot_id } პარტიაში { model_id } მოდელზე მოდელზე ქვა {request.POST.get('stone_full_name')} წარმატებით დაემატა.")
            return redirect('lot_update', lot_id=lot_id )

    return render(request, 'lot_model_stone_form.html', {'form': form, 'action': 'დამატება', 'lot_id':lot_id}, )


def lot_model_stone_change(request, lot_id, model_id, tmstmp, stone_full_name):

    lot_model_stone = get_object_or_404(LotModelStones, lot_id=lot_id, model_id=model_id, tmstmp=tmstmp, stone_full_name=stone_full_name)
    form = LotModelStonesForm(instance=lot_model_stone)

    if request.method == 'POST':
        form = LotModelStonesForm(request.POST)
        if form.is_valid():
            lot_model_stone.delete()
            form.save()
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
