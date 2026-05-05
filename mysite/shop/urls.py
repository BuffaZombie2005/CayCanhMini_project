"""URL configuration cho shop app."""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('tro-ly-ai/', views.chat_assistant, name='chat_assistant'),
    path('api/tro-ly-ai/', views.chat_assistant_send, name='chat_assistant_api'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Admin
    path('admin-dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/', views.product_admin_list, name='product_admin_list'),
    path('dashboard/products/create/', views.product_admin_create, name='product_admin_create'),
    path('dashboard/products/<int:pk>/edit/', views.product_admin_edit, name='product_admin_edit'),
    path('dashboard/products/<int:pk>/delete/', views.product_admin_delete, name='product_admin_delete'),
    path('dashboard/categories/', views.category_admin_list, name='category_admin_list'),
    path('dashboard/categories/create/', views.category_admin_create, name='category_admin_create'),
    path('dashboard/categories/<int:pk>/edit/', views.category_admin_edit, name='category_admin_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.category_admin_delete, name='category_admin_delete'),
    path('dashboard/orders/', views.order_admin_list, name='order_admin_list'),
    path('dashboard/orders/<uuid:order_id>/', views.order_admin_detail, name='order_admin_detail'),
]
