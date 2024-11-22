from django.urls import path
from .views import (
    owner_dashboard, waiter_order_form, submit_order,delete_menu_item,
    chef_dashboard, complete_order, register, user_login, user_logout,add_menu_item,waiter_notifications,generate_bill,menupage


)

urlpatterns = [
    path('owner/', owner_dashboard, name='owner_dashboard'),
    path('waiter/order/', waiter_order_form, name='waiter_order_form'),
    path('waiter/order/submit/', submit_order, name='submit_order'),
    path('chef/', chef_dashboard, name='chef_dashboard'),
    path('chef/order/complete/<int:order_id>/', complete_order, name='complete_order'),
    path('register/', register,name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('menu/add/', add_menu_item, name='add_menu_item'),
    path('menu/', menupage, name='menu'),
    path('menu/delete/<int:item_id>/', delete_menu_item, name='delete_menu_item'),

    path('waiter/notifications/', waiter_notifications, name='waiter_notifications'),
    path('owner/bill/<int:order_id>/', generate_bill, name='generate_bill'),


]