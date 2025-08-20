from django.urls import path
from . import views


urlpatterns = [
    # completed views

    # log in and log out
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),

    # in progress views

    # catalog
    path('catalog/', views.catalog, name='catalog'),
    path('model/create/', views.model_create, name='model_create'),
    path('model/<str:model_id>/update', views.model_update, name='model_update'),
    path('model/<str:model_id>/delete', views.model_delete, name='model_delete'),
    path('model/<str:model_id>/stone_add', views.model_stone_add, name='model_stone_add'),
    path('model/<str:model_id>/<str:stone_full_name>/stone_delete', views.model_stone_delete, name='model_stone_delete'),
    path('model/<str:model_id>/<int:lot_id>/2_lot_add', views.model_2_lot_add, name='model_2_lot_add'),

    # lot
    path('lot/', views.lot_list, name='lot_list'),
    path('lot/create/', views.lot_create, name='lot_create'),
    path('lot/<int:lot_id>/update/', views.lot_update, name='lot_update'),
    path('lot/<int:lot_id>/delete', views.lot_delete, name='lot_delete'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/model_update', views.lot_model_update, name='lot_model_update'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/<int:sold>/model_sold', views.lot_model_sold, name='lot_model_sold'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/model_delete', views.lot_model_delete, name='lot_model_delete'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/model_stone_add', views.lot_model_stone_add, name='lot_model_stone_add'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/<str:stone_full_name>/model_stone_change', views.lot_model_stone_change, name='lot_model_stone_change'),
    path('lot/<int:lot_id>/<str:model_id>/<str:tmstmp>/<str:stone_full_name>/model_stone_delete', views.lot_model_stone_delete, name='lot_model_stone_delete'),


    # transaction
    path('transaction_list/', views.transaction_list, name='transaction_list'),
    path('transaction_list/<str:transaction_type>/transaction_type/', views.transaction_list, name='transaction_type'),
    path('transaction/<str:transaction_type>/create/', views.transaction_create, name='transaction_create'),
    path('transaction/<str:tmstmp>/<str:item>/update/', views.transaction_update, name='transaction_update'),
    path('transaction/<str:tmstmp>/<str:item>/delete', views.transaction_delete, name='transaction_delete'),

    # other
    path('', views.home, name='home'),

    # TODO: to add views
    # add database users
]

# TODO: not needed for deployment delete later
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)