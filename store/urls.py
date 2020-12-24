from django.urls import path
from . import views

urlpatterns = [

    path('', views.store, name="store"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('add_product', views.add_product, name="add_product"),
    path('product_details/<int:pk>/', views.product_details, name="product_details"),
    path('product_details/<int:pk>/edit_product/', views.edit_product, name='edit_product'),

    path('product_details/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order")
]
