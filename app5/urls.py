from .views import login,mainPage,category,productview,category,categorywise,logout,AddtoCartView,ManageCartView,EmptyCartView

from .views import cartview, contact, signup, confirmation, sendmail, payment

from django.urls import path

urlpatterns = [
    path('login/',login,name = 'login'),
    path('signup/',signup,name='signup'),
    path('',mainPage,name = 'main'),
    path('category/',category,name = 'category'),
    path("product/<str:title>/",productview,name="prodetails"),
    path('categorywise/<str:title>/',categorywise),
    path('logout/',logout,name='logout'),
    path("add_to_cart-<int:pro_id>/",AddtoCartView.as_view(), name="addtocart"),
    path("my_cart/",cartview, name="mycart"),
    path("manage_cart/<int:cp_id>/",ManageCartView.as_view(), name="managecart"),
    path("empty_cart/",EmptyCartView.as_view(), name="emptycart"),
    path('contact/',contact,name='contact'),
    path('confirmation/',confirmation,name="confirmation"),
    path('sendmail/',sendmail,name='sendmail'),
    path('pay/',payment,name='PAYMENT'),
]


