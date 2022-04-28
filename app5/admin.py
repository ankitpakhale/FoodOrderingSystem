from django.contrib import admin
from .models import Registeration,Customer,Category,Products,Cart,CartProduct,Contact

admin.site.register([Registeration,Customer,Category,Products,Cart,CartProduct,Contact])