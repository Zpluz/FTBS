from django.urls import path
from . import views

app_name = 'ftbs'

urlpatterns = [
    path('home/', views.home, name='Home'),
    path('login/', views.ftbs_login, name='Login'),
    path('logout/', views.ftbs_logout, name='Logout'),
    path('signup/', views.signup, name='Sign up'),
    path('flights/', views.flight, name='Flights'),
    path('order/', views.order, name='Order'),
    path('profile/', views.profile, name='Profile'),
    path('myorders/', views.myorders, name='MyOrders'),
    path('orderinfo/', views.order_info, name='OrderInfo'),
]
