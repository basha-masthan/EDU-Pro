from django.urls import path
from .views import *

urlpatterns = [
    path('',home),
    path('about/',about),
    path('usredit/',usredit),
    path('contact/',contact),
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
    path('mb/',adminpage),
    path('delcard/',delcard),
    path('usrgd/',usrgd),
    path('mb/',adminpage),
    path('mb/course/',mb_course),
    path('mb/users/',mb_users),
]