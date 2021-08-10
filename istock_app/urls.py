from django.urls import path, include
from . import views

urlpatterns = [
    # =================================Products=================================
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('daily-reports/', views.daily_reports, name='daily-reports'),
    path('quick-links/', views.quick_links, name='quick-links'),
    path('all/products/', views.all_products, name='all_products'),
    path('Add/product/', views.add_product, name='add_product'),
    path('Update/product/<int:id>/', views.update_product, name='update_product'),
    path('View/product/<int:id>/', views.view_product, name='view_product'),
    path('Delete/product/<int:id>/', views.delete_product, name='delete_product'),

    # =================================Sales====================================
    path('sales/', views.all_sales, name='all_sales'),
    path('all-time/sales/', views.all_time_sales, name='all_time_sales'),
    path('Add/Sales/', views.add_sales, name='add_sales'),
    path('update_item/', views.updateItem, name='update_item'),
    path('Create/Invoice/<int:id>/Profoma', views.prepareProfomaInvoice, name='prepare_profoma_invoice'),
    path('Generated/Profoma-Invoice/<int:id>/', views.profomaInvoicePDF, name='profoma'),

    # ============================ Invoice ===========================================
    path('cancel/invoice/<int:id>/', views.cancel_invoice, name='cancel-invoice'),
    path('Generated/Profoma-Invoice/', views.profomaInvoicePDF, name='profoma'),

    # ============================ Invoice ===========================================
    path('cancel/invoice/<int:id>/', views.cancel_invoice, name='cancel-invoice'),
    path('Create/Invoice/<int:id>/', views.prepareInvoice, name='prepare_invoice'),
    path('Generated/Invoice/', views.invoicePDF, name='invoice'),
    path('Generated/<int:id>/Invoice/', views.reprintInvoicePDF, name='reprint-invoice'),
    path('Update/Sales/<int:id>/', views.update_sales, name='update_sales'),
    path('View/Sales/<int:id>/', views.view_sales, name='view_sales'),
    path('Delete/Sales/<int:id>/', views.delete_sales, name='delete_sales'),
    path('sales/report/', views.sales_report, name='sales_report'),
    path('print/sales/report/', views.salesReportPDF, name='print_sales_report'),
    # path('export/excel/', views.export_xls, name='export_excel'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('pdf/<int:id>', views.pdf, name='pdf'),
    path('daily-report-download/', views.daily_reports_PDF, name='daily-report-download'),


    # =======================Expenses ==========================================
    path('cash/', views.cash, name='cash'),
    path('expenses/', views.view_expenses, name='view_expenses'),
    path('add/expenses/', views.add_expenses, name='add_expenses'),
    path('Update/expense/<int:id>/', views.update_expense, name='update_expense'),
    path('delete/expense/<int:id>/', views.delete_expense, name='delete_expense'),
    path('actual/profit/', views.actual_profit, name='actual_profit'),

    # ================================ Percentages =============================
    path('percentages/', views.all_percentages, name = 'percentages'),
    path('add/percentages/', views.add_percentage, name = 'add_percentage'),
    path('apply/percentages/', views.priceApplied, name = 'price-applied'),
    path('update/percentages/<int:id>/', views.update_percentage, name = 'update_percentage'),
    path('delete/percentages/<int:id>/', views.delete_percentage, name = 'delete_percentage'),
    # ================================Purchases ================================
    path('all/purchases/', views.all_purchases, name='all_purchases'),
    path('ranged/purchases/', views.ranged_purchases, name='ranged_purchases'),
    path('add/purchases/', views.add_purchase, name='add_purchase'),
    path('update/purchases/<int:id>/', views.update_purchase, name='update_purchase'),
    path('view/purchases/<int:id>/', views.view_purchase, name='view_purchase'),
    path('delete/purchase/<int:id>/', views.delete_purchase, name='delete_purchase'),
    # ============================ Deposits ====================================
    path('deposit/', views.deposit, name='deposit'),
    path('deposits/', views.deposits, name='deposits'),
    path('delete/deposit/<int:id>/', views.deleteDeposit, name='delete_deposit'),
    # path('deposits/', views.deposit, name='deposit'),
]
