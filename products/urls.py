from django.urls import path
from .views import Home,Checkout,Product,add_to_cart,remove_from_cart,Register,OrderSummary,add_one_item_to_cart,remove_one_item_from_cart,PaymentView

urlpatterns=[
    path('',Home.as_view(), name="home"),
    path('register/', Register.as_view(),name="register"),
    path('product/<slug>/',Product.as_view(), name="product"),
    path('checkout/',Checkout.as_view(), name="checkout"),
    path('order_summary/',OrderSummary.as_view(), name="order_summary"),
    path('add_to_cart/<slug>/',add_to_cart, name="add_to_cart"),
    path('add_one_item_to_cart/<slug>/',add_one_item_to_cart, name="add_one_item_to_cart"),
    path('remove_one_item_from_cart/<slug>/',remove_one_item_from_cart, name="remove_one_item_from_cart"),
    path('remove_from_cart/<slug>/',remove_from_cart, name="remove_from_cart"),
    path('payment/<option>/',PaymentView.as_view(), name="payment"),

    
]
app_name="products"