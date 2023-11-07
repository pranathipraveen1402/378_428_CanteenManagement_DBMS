from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home,name="home"),
    path('user/', views.userPage, name="user-page"),
    path('register/',views.registerPage,name="register"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('products/',views.products,name="products"),
    path('customer/<str:pk>/',views.customer,name="customer"),
    path('account/',views.accountSettings,name="account"),
    path('create_order/<str:pk>/',views.createOrder,name="create_order"),
    path('update_order/<str:pk>/',views.updateOrder,name="update_order"),
    path('delete_order/<str:pk>/',views.deleteOrder,name="delete_order"),
    path('store/',views.store,name="store"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('process_order/',views.processOrder,name="process_order"),
    path('update_item/',views.updateItem,name="update_item"),
    

    #path('reset_password/',auth_views.PasswordResetView.as_view(),name="reset_password"),
    #path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(),name = "password_reset_done"),
    #path('reset_password/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name = "password_reset_confirm"),
   # path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(),name="password_reset_complete"), """
]