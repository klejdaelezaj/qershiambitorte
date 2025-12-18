from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="products"),
    path('about-us/', views.about_us, name='about_us'),
    path("contact-us/", views.contact_us, name="contact_us"),
    path('accounts/login/', views.client_login, name='client_login'),
    path('logout/', views.client_logout, name='client_logout'),
    path('create_order/', views.create_order_from_cart, name='create_order_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('register/', views.register_view, name='register'),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/<int:order_id>/", views.checkout, name="checkout"),
    path('checkout/', views.cart_checkout, name='cart_checkout'),
    path("success/<int:order_id>/", views.success, name="success"),
    path("search/", views.product_search, name="product_search"),
    path("favorites/", views.favorite_list, name="favorite_list"),
    path("favorites/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path('make_order/', views.create_order_from_cart, name='make_order'),
    path("test-email/", views.test_email_view),

]



