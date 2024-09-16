from django.urls import path
from .views import *

urlpatterns = [
    path('',home),
    path('about/',about),
    path('usredit/',usredit),
    path('contact/',contact),
    path('msg/',msg),
    path('otp/',uotp),
    path('register/',register),
    path('usrpage/',usrpage),
    path('login/',login),
    path('Auth_otp/',Auth_otp),
    path('usrp/',usrp),
    path('logout/',logout_1),
    path('cart/',usr_cart),
    path('payment/',payment),
    path('cartadd/',usrcart_add),
    path('admin/',adminpage),
    path('delcard/',delcard),
    path('usrgd/',usrgd),
    path('admin/',adminpage),
    path('admin/users/',mb_users),
    path('admin/courses/',mb_course),
    path('admin/msg/',msgs),
]