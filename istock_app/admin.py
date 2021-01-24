# from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(products)
admin.site.register(sales)
admin.site.register(OrderItem)
admin.site.register(Purchase)
admin.site.register(Deposit)
admin.site.register(Expenses)
admin.site.register(Percentages)

# @admin.register(sales)
# class salesAdmin(ImportExportModelAdmin):
#     pass
#
# @admin.register(products)
# class productsAdmin(ImportExportModelAdmin):
#     pass
#
# @admin.register(Purchase)
# class purchaseAdmin(ImportExportModelAdmin):
#     pass
#
# @admin.register(Deposit)
# class depositAdmin(ImportExportModelAdmin):
#     pass
