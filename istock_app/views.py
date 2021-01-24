from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import json
import urllib.request
from datetime import datetime, timedelta, date
from django.contrib import messages
from tablib import Dataset
from .require import renderPdf
from django.views import View
from .models import *
from .forms import *
from django.db.models import F, Q
import xlwt
from django.contrib.auth.models import User
import locale
from django.contrib.auth.decorators import login_required
from accounts.decorators import *


# Create your views here.
def home(request):
    myTemplate = 'istock/home.html'
    context = {

    }
    return render(request, myTemplate, context)

@admin_login_required
def dashboard(request):
    products_data  = products.objects.all()
    products_number = products_data.count()

    now = datetime.now()
    this_month = datetime.now().month
    this_year = datetime.now().year

    purchases_data  = Purchase.objects.filter(date__year = this_year, date__month = this_month)
    sales_data  = sales.objects.filter(date_added__year = this_year, date_added__month = this_month)
    expenses_data  = Expenses.objects.filter(date__year = this_year, date__month = this_month)

    expenses_amount = sum([expense.amount for expense in expenses_data])
    purchases_amount = sum([purchase.totalprice for purchase in purchases_data])


    sales_amount = sum([sale.get_total_amount for sale in sales_data])
    total_buying_price = sum([sale.total_buying_price for sale in sales_data])
    gross_profit = sales_amount - total_buying_price
    net_profit = gross_profit - expenses_amount

    sales_year  = sales.objects.filter(date_added__year = this_year)
    expenses_year  = Expenses.objects.filter(date__year = this_year)
    purchases_year  = Purchase.objects.filter(date__year = this_year)

    months = [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

    # Expenses
    expenses_count = []
    for i in range(1,12):
        expenses_amount_monthly = 0
        expenses_monthly = expenses_year.filter(date__month = i)
        for expense in expenses_monthly:
            expenses_amount_monthly = sum([expense.amount for expense in expenses_monthly])
        expenses_count.append(expenses_amount_monthly)

    # Sales
    sales_count = []
    for i in range(1,13):
        sales_amount_monthly = 0
        sales_monthly = (sales_year.filter(date_added__month = i))
        for sale in sales_monthly:
            sales_amount_monthly = sum([sale.get_total_amount for sale in sales_monthly])
        sales_count.append(sales_amount_monthly)

    # Purchases
    purchases_count = []
    for i in range(1,13):
        purchases_amount_monthly = 0
        purchases_monthly = (purchases_year.filter(date__month = i))
        for purchase in purchases_monthly:
            purchases_amount_monthly = sum([purchase.total_price for purchase in purchases_monthly])
        purchases_count.append(purchases_amount_monthly)

    # Profit
    profit_count = []
    for i in range(1,13):
        profit_amount_monthly = 0
        sales_monthly = (sales_year.filter(date_added__month = i))
        expenses_monthly = expenses_year.filter(date__month = i)
        profit_amount_monthly = 0
        for sale in sales_monthly:
            sales_amount_monthly = sum([sale.get_total_amount for sale in sales_monthly])
            total_buying_price_monthly = sum([sale.total_buying_price for sale in sales_monthly])
            expenses_amount_monthly = sum([expense.amount for expense in expenses_monthly])
            gross_profit = sales_amount_monthly - total_buying_price_monthly
            profit_amount_monthly = gross_profit - expenses_amount_monthly
        profit_count.append(profit_amount_monthly)

    myTemplate = 'istock/dashboard.html'
    context = {
        'purchases_amount': purchases_amount,
        'sales_amount': sales_amount,
        'expenses_amount': expenses_amount,
        'profit': net_profit,
        'products_number': products_number,
        'sales_year': sales_year,
        'sales_count': sales_count,
        'expenses_count': expenses_count,
        'profit_count': profit_count,
        'purchases_count': purchases_count,
        'months': months,
    }
    return render(request, myTemplate, context)


def quick_links(request):
    myTemplate = 'istock/quickLinks.html'
    context = {
    }
    return render(request, myTemplate, context)

@login_required
def all_products(request):
    all_products = products.objects.all().order_by('-id')
    low = [product for product in all_products if product.quantity < 10]
    query = request.GET.get("q")
    if query:
        all_products = products.objects.filter(Q(product_name__icontains = query) | Q(code__icontains = query)).order_by('-id')
        if not all_products:
            all_products = products.objects.all().order_by('-id')
            messages.warning(request,f'Invalid Search!')


    context = {
        'myProducts': all_products,
        'low': low
    }
    myTemplate = 'istock/allProducts.html'
    return render (request, myTemplate, context)

 # ==================================Products Functions==================================
@login_required
def add_product(request):
    form = addProductForm()
    if request.method == 'POST':
        form = addProductForm(request.POST)
        get_name = request.POST.get('product_name')
        get_quantity = request.POST.get('quantity')
        get_buying_price = request.POST.get('buying_price')
        get_selling_price = request.POST.get('selling_price')
        get_vendor = request.POST.get('vendor')

        # blocking repition of product names
        try:
            check_name = products.objects.get(product_name = get_name)
            messages.success(request, f'Product with this name already exist! We recommend you to top up to the existing quantity in the stock')
            return redirect('add_product')
        except products.DoesNotExist:
            if form.is_valid():
                form.save()
                messages.success(request, f'Product added successfully')
                return redirect('add_product')
    else:
        form = addProductForm()
    context = {
        'form': form
    }
    myTemplate = 'istock/addProduct.html'
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def update_product(request, id):
    instance = get_object_or_404(products, pk = id)
    form = updateProductForm(request.POST or None, instance = instance)
    # print(form.product_name)
    if request.method == 'POST':
        get_name = request.POST.get('product_name')
        get_quantity = request.POST.get('quantity')
        get_buying_price = request.POST.get('buying_price_per_each')
        get_selling_price = request.POST.get('selling_price_per_each')

        # update quantity
        if form.is_valid():
            # instance.quantity += int(get_quantity)
            # instance.save()
            form.save()
            messages.success(request, f'Product has been updated successifully!')
            return redirect ('all_products')
    context = {
        'form': form,
    }
    myTemplate = 'istock/updateProduct.html'
    return render(request, myTemplate, context)

@login_required
def view_product(request, id):
    get_data = get_object_or_404(products, pk = id)

    # Calculations for total costs incured and expected to income.
    quantity = get_data.quantity
    buying_price = get_data.buying_price_per_each
    selling_price = get_data.selling_price_per_each
    total_buying_price = buying_price*quantity
    total_selling_price = selling_price*quantity
    profit_expected = total_selling_price - total_buying_price

    context = {
        'myProduct': get_data,
        'buying_price': total_buying_price,
        'selling_price': total_selling_price,
        'profit': profit_expected,
    }
    myTemplate =  'istock/viewProduct.html'
    return render(request,myTemplate,context)


# Delete Product
@login_required
@admin_login_required
def delete_product(request, id):
    get_data = get_object_or_404(products, pk = id)
    get_data.delete()
    messages.success(request, f'Product deleted successfull!')
    return redirect('all_products')


# =======================================Sales Functions=======================================
@login_required
def all_sales(request):
    orders = sales.objects.all()
    for order in orders:
        if order.get_cart_items <= 0 or order.profoma == True:
            order.delete()

    all_sales = sales.objects.all().order_by('-id')

    query = request.GET.get("q")
    if query:
        all_sales = sales.objects.filter(Q(id__icontains = query)).order_by('-id')
        if not all_sales:
            all_sales = products.objects.all().order_by('-id')
            messages.warning(request,f'Invalid Search!')
    context = {
        'mySales': all_sales
    }
    myTemplate = 'istock/sales.html'
    return render (request, myTemplate, context)

# def sell(request):
#     form = addSalesForm()

@login_required
@shopkeeper_login_required
def add_sales(request):
    all_products = products.objects.all()
    query = request.GET.get("q")
    if query:
        all_products = all_products.filter(Q(product_name__icontains = query) | Q(code__icontains = query))
        if not all_products:
            messages.warning(request, f'No results found!!')
            all_products = products.objects.all()


    # cart
    order, created = sales.objects.get_or_create(seller = request.user, ordered = False)
    items = order.orderitem_set.all()
    # items = []

    orders = sales.objects.all()
    for order in orders:
        if order.get_cart_items <= 0 or order.profoma:
            order.delete()


    context = {
        'products': all_products,
        'items': items,
        'order': order,
    }
    myTemplate = 'istock/addSales.html'
    return render(request, myTemplate, context)

@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('ProductId: ', productId)
    print('Action: ', action)

    orders = sales.objects.all()

    product = products.objects.get(id = productId)
    order, created = sales.objects.get_or_create(seller = request.user, ordered = False, profoma = False)

    orderItem, created = OrderItem.objects.get_or_create(sale = order, product = product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.price = product.selling_price_per_each
    orderItem.buying_price = product.buying_price_per_each
    orderItem.product_name = product.product_name

    orderItem.save()


    if orderItem.quantity <= 0 or action == 'delete':
        orderItem.delete()

    for order in orders:
        if order.get_cart_items <= 0 or order.profoma:
            order.delete()

    return JsonResponse('Item was added', safe=False)



@login_required
@shopkeeper_login_required
def update_sales(request, id):
    instance = get_object_or_404(sales, pk = id)

    form = addSalesForm(request.POST or None, instance = instance)

    order = instance.orderitem_set.all()
    if request.method == 'POST':
        for item in order:
            if request.POST.get(item.product.product_name):
                quantity_update = int(request.POST.get(item.product.product_name))

                product = get_object_or_404(products, pk = item.product.id)

                print('Earlier: ', product.quantity)
                print('Item: ', item.quantity)

                increased = increase_product_function(item.product.id, item.quantity)
                print('After Increasing: ', increased)
                product.quantity = increased
                product.save()

                product.save()

                item.quantity = quantity_update
                item.save()

                decreased = decrease_product_function(item.product.id, quantity_update)
                print('After Decreasing: ',decreased)
                product.quantity = decreased
                product.save()
                product.save()
            else:
                messages.warning(request, f'Sales wasn\'t updated!')
                return redirect ('all_sales')

        if form.is_valid():
            messages.success(request, f'Sales has been made successifully!')

            # messages.success(request, f'Sales has been updated successifully!')
            form.save()
            return redirect ('all_sales')
    context = {
        'form': form,
        'order': order,
    }
    myTemplate = 'istock/updateSales.html'
    return render(request, myTemplate, context)

@login_required
def view_sales(request, id):
    get_data = get_object_or_404(sales, pk=id)
    context = {
        'mySales': get_data,
    }
    myTemplate =  'istock/viewSingleSales.html'
    return render(request, myTemplate, context)

@login_required
@shopkeeper_login_required
def prepareInvoice(request, id):
    order = sales.objects.get(id = id)
    orderItems = order.orderitem_set.all()
    print(products)
    for item in orderItems:
        print(item.product.id)
        product = get_object_or_404(products, pk = item.product.id)
        if item.quantity > product.quantity:
            messages.warning(request, f'Can\'t sell some products since order quantity in greater than what is available, cross check before creating an order!!')
            return redirect('all_products')

    for item in orderItems:
        deacreased_quantity = decrease_product_function(item.product.id, item.quantity)
        print('This is original Quantity ', deacreased_quantity)

    order.ordered = True
    order.save()

    orders = sales.objects.all()
    for order in orders:
        if order.get_total_amount <= 0 or order.profoma:
            order.delete()

    form = addSalesForm(request.POST or None)
    myTemplate = 'istock/invoice/prepareInvoice.html'

    context = {
        'form': form,
        'order': order,
        'orderItems': orderItems,
    }
    return render(request, myTemplate, context)

@login_required
def prepareProfomaInvoice(request, id):
    order = sales.objects.get(id = id)
    order.profoma = True
    order.save()
    order.ordered = True
    order.save()

    orderItems = order.orderitem_set.all()
    # Delete all orders that have nothing
    orders = sales.objects.all()
    for ordery in orders:
        if ordery.get_total_amount <= 0:
            ordery.delete()

    form = addSalesForm(request.POST or None)
    myTemplate = 'istock/invoice/prepareInvoice.html'
    context = {
        'order': order,
        'form': form,
        'orderItems': orderItems,
    }
    return render(request, myTemplate, context)


# Delete Sales
@login_required
@shopkeeper_login_required
def cancel_invoice(request, id):
    invoice = get_object_or_404(sales, pk = id)

    items = invoice.orderitem_set.all()
    print('Items: ', items)
    for item in items:
        print(item)
        product = get_object_or_404(products, id = item.product.id)
        increased = increase_product_function(item.product.id, item.quantity)
        product.quantity = increased
        product.save()
    invoice.delete()
    messages.warning(request, f'Order cancelled!!')
    return redirect('all_sales')


@login_required
@admin_login_required
def delete_sales(request, id):
    get_data = get_object_or_404(sales, pk = id)
    get_data.delete()
    messages.success(request, f'Sales deleted successfull!')
    return redirect('all_sales')


def increase_product_function( id, replaced_quantity):
    id = int(id)
    last_quantity = int(replaced_quantity)
    # filtered_product = products.objects.filter(pk = id)
    get_product = get_object_or_404(products, pk = id)

    get_product.quantity += last_quantity
    # filtered_product.update(quantity = get_product.quantity)
    filtered_product = products.objects.filter(pk = id)
    get_product = get_object_or_404(products, pk = id)

    get_product.quantity += last_quantity
    filtered_product.update(quantity = get_product.quantity)
    get_product.save()
    return  get_product.quantity


def decrease_product_function( id, replaced_quantity):
    id = int(id)
    last_quantity = int(replaced_quantity)
    filtered_product = products.objects.filter(pk = id)
    get_product = get_object_or_404(products, pk = id)

    if get_product.quantity >= last_quantity:
        get_product.quantity -= last_quantity
        filtered_product.update(quantity = get_product.quantity)
        get_product.save()
        return  get_product.quantity
    else:
        return None

def calculate_buying_price( id, quantity, total_price):
    get_name = int(id)
    get_quantity = int(quantity)
    get_price = int(total_price)

    buying_price = get_price/get_quantity
    all_percentages = Percentages.objects.all()
    percentages = 0
    for percentage in all_percentages:
        percentages += percentage.percent
    selling_price = (percentages/100)*buying_price + buying_price

    filtered_product = products.objects.filter(pk = get_name)

    get_product = get_object_or_404(products, pk = get_name)
    # get_product.buying_price_per_each = buying_price
    filtered_product.update(buying_price_per_each = buying_price)
    filtered_product.update(selling_price_per_each = selling_price)
    return  get_product.buying_price_per_each

def vatCalc():
    all_sales = sales.objects.all()
    expenses = Expenses.objects.all()
    all_products = products.objects.all()
    total_sales_amount = sum([sale.get_total_amount for sale in all_sales])
    total_expenses = sum([expense.amount for expense in expenses])
    total_buying_amount = 0
    for sale in all_sales:
        total_buying_amount += sum([item.buying_price for item in sale.order])

    usable_amount = total_buying_amount + total_expenses

    net_amount = total_sales_amount - usable_amount
    vat = (18/100) * net_amount
    return vat

def priceApplied(request):
    all_products = products.objects.all()
    all_percentages = Percentages.objects.all()
    for product in all_products:
        percentages = sum([percentage.percent for percentage in all_percentages])
        profit = (product.selling_price_per_each - product.buying_price_per_each)/product.buying_price_per_each * 100

        if product.buying_price_per_each == product.selling_price_per_each or product.selling_price_per_each == 0 or profit < percentages:


            selling_price = (percentages/100)*product.buying_price_per_each + product.buying_price_per_each
            product.selling_price_per_each = selling_price
            product.save()
    messages.success(request, f'Percentages applied successifully!')
    return redirect ('percentages')



#=============== Expenses=======================================================
@login_required
@shopkeeper_login_required
def add_expenses(request):
    form = addExpensesForm(request.POST or None)
    if request.method == 'POST':
        form = addExpensesForm(request.POST or None)
        get_name = request.POST.get('expense')
        get_quantity = request.POST.get('description')
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense added successfully')
            return redirect('add_expenses')
    context = {
        'form': form,
    }
    myTemplate = 'istock/addExpenses.html'
    return render(request, myTemplate, context)


@login_required
def view_expenses(request):
    get_expenses = Expenses.objects.all().order_by('-id')
    query = request.GET.get("q")
    if query:
        get_expenses = Expenses.objects.filter(date__icontains = query).order_by('-id')
        if not get_expenses:
            get_expenses = Expenses.objects.all().order_by('-id')
            messages.warning(request,f'Invalid Search!')

    context = {
        'expenses': get_expenses,
    }
    myTemplate = 'istock/viewExpenses.html'
    return render(request, myTemplate, context)

@login_required
@shopkeeper_login_required
def update_expense(request, id):
    instance = get_object_or_404(Expenses, pk = id)
    form = addExpensesForm(request.POST or None, instance = instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense has been updated successifully!')
            return redirect ('view_expenses')
    context = {
        'form': form,
    }
    myTemplate = 'istock/addExpenses.html'
    return render(request, myTemplate, context)

@login_required
@shopkeeper_login_required
def delete_expense(request, id):
    get_data = get_object_or_404(Expenses, pk = id)
    get_data.delete()
    messages.success(request, f'Expense deleted successfull!')
    return redirect('view_expenses')

def total_expenses():
    expenses = Expenses.objects.all()
    total = 0
    for expense in expenses:
        total += expense.amount
    return total


def total_sales():
    get_sales = sales.objects.all()
    total = 0
    for sale in get_sales:
        total += sale.get_total_amount
    return total

@login_required
def cash(request):
    get_sales = sales.objects.all()
    buying_amount = sum([sale.total_buying_price for sale in get_sales])
    available_amount = total_sales() - buying_amount
    cash = available_amount - total_expenses()
    net_cash = cash - vatCalc()
    if cash <= 0:
        messages.info(request, f'You have excessive expenditures. Watch out, you are getting down!')
    myTemplate = 'istock/cash.html'
    context = {
        'cash': cash,
        'total_cash': available_amount,
        'expenses': total_expenses(),
        'vat': vatCalc(),
        'net_cash': net_cash,
    }
    return render(request, myTemplate, context)
#==================End expenses=================================================
@login_required
@shopkeeper_login_required
def sales_report(request):
    if request.method == 'POST':
        if request.POST.get('start_date') == "" or request.POST.get('end_date') == "":
            messages.success(request, f'Please provide both start date and end date!')
            return redirect('sales_report')
        else:
            get_start_date = datetime.strptime (request.POST.get('start_date'), '%Y-%m-%d')
            get_end_date =  datetime.strptime (request.POST.get('end_date'), '%Y-%m-%d')
                            # datetime.strptime (request.POST.get('appointment_date'), '%Y-%m-%d')
            # ranged_data = time_calculator(get_start_date, get_end_date)
            total_sales = 0
            total_buying_price = 0
            price_per_product = 0
            totalCalc = []
            get_data = sales.objects.filter(date_added__range = [ get_start_date, get_end_date])
            for data in get_data:
                total_sales += data.get_total_amount
                items = data.order
                for item in items:
                    total_buying_price += item.buying_price * item.quantity
            total_profit = total_sales - total_buying_price
            vat = (18/100) * total_profit
            net_profit = total_profit - vat
            total_sales_number = get_data.count()
        context = {
        'sales': get_data,
        'total_sales': total_sales,
        'total_buying_price': total_buying_price,
        'total_profit': total_profit,
        'vat': vat,
        'net_profit': net_profit,
        'start_date': get_start_date,
        'end_date': get_end_date,
        'total_products': total_sales_number,
        }
        myTemplate = 'istock/salesReport.html'
        return render (request, myTemplate, context)
    context = {}
    myTemplate = 'istock/salesReport.html'
    return render (request, myTemplate, context)



    # =================================Purchases=================================
@login_required
def all_purchases(request):
    get_purchases = Purchase.objects.all().order_by('-id')
    query = request.GET.get("q")
    if query:
        get_purchases = Purchase.objects.filter(Q(date__icontains = query)).order_by('-id')
        if not all_sales:
            all_sales = Purchase.objects.objects.all().order_by('-id')
            messages.warning(request,f'Invalid Search!')
    context = {
        'purchases': get_purchases,
    }
    myTemplate = 'istock/allPurchases.html'
    return render(request, myTemplate, context)

@login_required
@shopkeeper_login_required
def add_purchase(request):
    form = addPurchaseForm()
    if request.method == 'POST':
        form = addPurchaseForm(request.POST or None)
        get_name = int(request.POST.get('product'))
        print(get_name)
        get_quantity = int(request.POST.get('quantity'))
        get_date = request.POST.get('date')
        get_total_price = request.POST.get('total_price')
        if form.is_valid():
            get_product = get_object_or_404(products, pk = get_name)
            after = get_quantity + get_product.quantity
            form = Purchase(
                product = get_product,
                product_name = get_product.product_name,
                quantity = get_quantity,
                quantity_before = get_product.quantity,
                quantity_after = after,
                total_price = get_total_price,
                date = get_date
            )
            form.save()
            increase_product_function(get_product.id, get_quantity)
            calculate_buying_price(get_name, get_quantity, get_total_price)
            messages.success(request, f'Purchase added successfully!')
            return redirect('add_purchase')

    context = {
     'form': form
    }
    myTemplate = 'istock/addPurchases.html'
    return render(request, myTemplate, context)

@login_required
@shopkeeper_login_required
def update_purchase(request, id):
    instance = get_object_or_404(Purchase, pk = id)

    form = addPurchaseForm(request.POST or None, instance = instance)
    # quantity = roll_back_product_function(instance.id, instance.quantity)

    if request.method == 'POST':
        get_name = int(request.POST.get('product_name'))
        get_quantity = request.POST.get('quantity')
        get_total_price = request.POST.get('total_price')
        get_date = request.POST.get('date')
        get_product = get_object_or_404(products, pk = get_name)
        new_quantity = get_product.quantity - instance.quantity
        if new_quantity < 0:
            messages.warning(request, f'Can\'t Update, quantity filled was not correct')
            return redirect('all_purchases')
        filtered_product = products.objects.filter(pk = get_name)
        filtered_product.update(quantity = new_quantity)
        if form.is_valid():
            filtered_object = Purchase.objects.filter(id = instance.id)
            form.save()
            increase_product_function(get_name, get_quantity)
            calculate_buying_price(get_name, get_quantity, get_total_price)
            messages.success(request, f'Purchase has been updated successifully!')
            return redirect ('all_purchases')
    context = {
        'form': form,
    }
    myTemplate = 'istock/addPurchases.html'
    return render(request, myTemplate, context)

@login_required
def view_purchase(request, id):
    get_data = get_object_or_404(Purchase, pk = id)
    context = {
        'purchase': get_data,
    }
    myTemplate =  'istock/viewSinglePurchase.html'
    return render(request,myTemplate,context)



# Delete Purchase
@login_required
@shopkeeper_login_required
def delete_purchase(request, id):
    get_data = get_object_or_404(Purchase, pk = id)
    get_data.delete()
    messages.success(request, f'Purchase deleted successfull!')
    return redirect('all_purchases')

@login_required
def ranged_purchases(request):
    if request.method == 'POST':
        if request.POST.get('start_date') == "" or request.POST.get('end_date') == "":
            messages.success(request, f'Please provide both start date and end date!')
            return redirect('sales_report')
        else:
            get_start_date = datetime.strptime (request.POST.get('start_date'), '%Y-%m-%d')
            get_end_date =  datetime.strptime (request.POST.get('end_date'), '%Y-%m-%d')


            total_price= 0
            get_data = Purchase.objects.filter(date__range = [get_start_date, get_end_date])
            for data in get_data:
                total_price += data.total_price
            total_purchases = get_data.count()
        context = {
            'purchases': get_data,
            'total_price': total_price,
            'start_date': get_start_date,
            'end_date': get_end_date,
            'total_purchases': total_purchases,
        }
        myTemplate = 'istock/rangedPurchases.html'
        return render (request, myTemplate, context)
    context = {}
    myTemplate = 'istock/rangedPurchases.html'
    return render (request, myTemplate, context)




@login_required
def actual_profit(request):
    if request.method == 'POST':
        get_start_date = datetime.date(datetime.strptime (request.POST.get('first_date'), '%Y-%m-%d'))
        get_end_date =  datetime.date(datetime.strptime (request.POST.get('last_date'), '%Y-%m-%d'))
        other_expenses =  int(request.POST.get('expenses'))
        get_data = sales.objects.filter(date_added__range = [get_start_date, get_end_date])
        print('Sales obtained', get_data)
        total_sales = 0
        total_buying_price = 0
        for data in get_data:
            total_sales += data.get_total_amount
            items = data.order
            print(data.order)
            for item in items:
                total_buying_price += item.buying_price * item.quantity

        print(total_buying_price)
        print(total_sales)
        total_profit = total_sales - total_buying_price
        actual_profit = total_profit - other_expenses
        context = {
            'start_date': get_start_date,
            'end_date': get_end_date,
            'total_profit': total_profit,
            'other_expenses': other_expenses,
            'actual_profit': actual_profit,
        }
        myTemplate = 'istock/profitView2.html'
        return render(request, myTemplate, context)
    total_expenses =sum([expense.amount for expense in Expenses.objects.all()])
    context = {
    'expenses': total_expenses,
    }
    myTemplate = 'istock/profitView.html'
    return render(request, myTemplate, context)


@login_required
def deposit(request):
    if request.method == 'POST':
        get_start_date = datetime.strptime (request.POST.get('start_date'), '%Y-%m-%d').date()
        get_end_date =  datetime.strptime (request.POST.get('end_date'), '%Y-%m-%d').date()
        actual_profit = float(request.POST.get('actual_profit'))
        reduced = float(request.POST.get('reduced'))
        bank = request.POST.get('bank')
        deposition_date = datetime.now().date()
        deposit = actual_profit - reduced
        print(get_start_date)
        print(get_end_date)
        print(actual_profit)
        print(reduced)
        print(bank)
        get_data = Deposit.objects.filter(first_date__range = [ get_start_date, get_end_date])
        get_data1 = Deposit.objects.filter(last_date__range = [ get_start_date, get_end_date])
        if get_data or get_data1:
            messages.warning(request, f'Some dates are already deposited!')
            return redirect('actual_profit')
        elif deposit <= 0:
            messages.warning(request, f'Can\'t deposit this amount!')
            return redirect('actual_profit')
        else:

            form = Deposit (
                first_date = get_start_date,
                last_date = get_end_date,
                deposition_date = deposition_date,
                amount = deposit,
                bank = bank,
                deposited_by = request.user
            )
            form.save()
            messages.success(request, f'Amount deposited successfully')
            return redirect('actual_profit')

@login_required
def deposits(request):
    deposits = Deposit.objects.all()
    # user = request.user
    # total_deposits = user.deposit_set.all()
    # total_amount_deposited = sum([deposit.amount for deposit in total_deposits])
    total_amount_deposited = sum([deposit.amount for deposit in deposits])

    myTemplate = 'istock/deposits.html'
    context = {
        'deposits': deposits,
        'amount': total_amount_deposited,
    }
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def deleteDeposit(request, id):
    deposit = get_object_or_404(Deposit, id = id)
    deposit.delete()
    messages.success(request, f'Deposit deleted successfully')
    return redirect('deposits')

@login_required
@admin_login_required
def all_percentages(request):
    get_percentages = Percentages.objects.all()
    myTemplate = 'istock/viewPercentages.html'
    context = {
        'percentages': get_percentages,
    }
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def add_percentage(request):
    form = addPercentageForm()
    if request.method == 'POST':
        form = addPercentageForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, f'Percentage type added successfully!')
            return redirect('add_percentage')

    context = {
     'form': form
    }
    myTemplate = 'istock/addPercentage.html'
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def update_percentage(request, id):
    instance = get_object_or_404(Percentages, pk = id)
    form = addPercentageForm(request.POST or None, instance = instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Percentage type has been updated successifully!')
            return redirect ('percentages')
    context = {
        'form': form,
    }
    myTemplate = 'istock/addPercentage.html'
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def delete_percentage(request, id):
    get_data = get_object_or_404(Percentages, pk = id)
    get_data.delete()
    messages.success(request, f'Percentage deleted successfull!')
    return redirect('percentages')

# =====================================FILES=====================================

def render_to_pdf(template_src, context = {}):
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type = 'application/pdf')
    return None


def invoicePDF(request):
    if request.method == 'POST':
        order_id = request.POST.get('order')
        name = request.POST.get('name')

        order = sales.objects.get(id = order_id)
        order.customer_name = name
        order.ordered = True
        order.save()

        orders = sales.objects.all()
        for order in orders:
            if order.get_cart_items <= 0:
                order.delete()
        myTemplate = 'istock/invoice/invoice.html'
        context = {
            'sales': order,
        }
        pdf = render_to_pdf(myTemplate, context)
        # if pdf:
        #     return HttpResponse(pdf, content_type = 'application/pdf')
        # else:
        #     return HttpResponse('Not found')
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f'{order.customer_name} Invoice.pdf'
            content = f"attachment; filename = {filename} "
            response['Content-Disposition'] = content
            if response:
                return response
            else:
                return HttpResponse('Not found')

def reprintInvoicePDF(request, id):
        order = get_object_or_404(sales, pk = id)
        myTemplate = 'istock/invoice/invoice.html'
        context = {
            'sales': order,
        }
        pdf = render_to_pdf(myTemplate, context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f'{order.customer_name} Invoice.pdf'
            content = f"attachment; filename = {filename} "
            response['Content-Disposition'] = content
            if response:
                return response
            else:
                return HttpResponse('Not found')


def profomaInvoicePDF(request, id):
    if request.method == 'POST':
        order = get_object_or_404(sales, pk=id)
        customer_name = request.POST.get('customer_name')
        physical_address = request.POST.get('physical_address')
        postal_address = request.POST.get('postal_address')
        customer_TIN = request.POST.get('customer_TIN')
        customer_VRN = request.POST.get('customer_VRN')


        # order = sales.objects.get(id = order_id)
        order.customer_name = customer_name
        order.save()
        order.physical_address = physical_address
        order.save()
        order.postal_address = postal_address
        order.save()
        order.customer_TIN = customer_TIN
        order.save()
        order.customer_VRN = customer_VRN
        order.save()


        form = addSalesForm(request.POST or None)

        if form.is_valid():
            form.save()


        orderItems = order.orderitem_set.all()

        for item in orderItems:
            print('Before ',item.quantity)
            if request.POST.get(item.product.product_name):
                quantity_update = int(request.POST.get(item.product.product_name))
                item.quantity = quantity_update
                item.save()
                print('After ',item.quantity)

        # order = get_object_or_404(sales, pk=id)
        orders = sales.objects.all()
        for ordery in orders:
            if ordery.get_cart_items <= 0:
                ordery.delete()


        myTemplate = 'istock/invoice/profomaInvoice.html'
        context = {
            'sales': order,
        }
        pdf = render_to_pdf(myTemplate, context)
        # if pdf:
        #     return HttpResponse(pdf, content_type = 'application/pdf')
        # else:
        #     return HttpResponse('Not found')
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f'{order.customer_name} Profoma Invoice.pdf'
            content = f"attachment; filename = {filename} "
            response['Content-Disposition'] = content
            if response:
                return response
            else:
                return HttpResponse('Not found')

def salesReportPDF(request):
        if request.method == 'POST':
            get_start_date = datetime.strptime (request.POST.get('start_date'), '%Y-%m-%d')
            get_end_date =  datetime.strptime (request.POST.get('end_date'), '%Y-%m-%d')
                            # datetime.strptime (request.POST.get('appointment_date'), '%Y-%m-%d')
            # ranged_data = time_calculator(get_start_date, get_end_date)
            total_sales = 0
            total_buying_price = 0
            price_per_product = 0
            totalCalc = []
            get_data = sales.objects.filter(date_added__range = [ get_start_date, get_end_date])
            for data in get_data:
                total_sales += data.get_total_amount
                items = data.order
                for item in items:
                    total_buying_price += item.product.buying_price_per_each * item.quantity
            total_profit = total_sales - total_buying_price
            vat = (18/100) * total_profit
            net_profit = total_profit - vat
            total_sales_number = get_data.count()

            context = {
            'sales': get_data,
            'total_sales': total_sales,
            'total_buying_price': total_buying_price,
            'total_profit': total_profit,
            'vat': vat,
            'net_profit': net_profit,
            'start_date': get_start_date,
            'end_date': get_end_date,
            'total_products': total_sales_number,
            'user': request.user,
            }

            myTemplate = 'istock/invoice/sales_report.html'
            pdf = render_to_pdf(myTemplate, context)
            # if pdf:
            #     return HttpResponse(pdf, content_type = 'application/pdf')
            # else:
            #     return HttpResponse('Not found')
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = f'Sales Report {get_start_date.day}-{get_start_date.month}-{get_start_date.year} To {get_end_date.day}-{get_end_date.month}-{get_start_date.year}.pdf'
                content = f"attachment; filename = {filename} "
                response['Content-Disposition'] = content
                if response:
                    return response
                else:
                    return HttpResponse('Not found')




@login_required
class pdf(View):
    def get(self, request, id):
        single_record = get_object_or_404(sales, id = id)
        try:
            selling_price = single_record.sales_name.selling_price_per_each * single_record.quantity
        except:
            Http404('Content Not Found')
        context = {
            'sales': single_record,
            'total_amount': selling_price
        }
        doc = renderPdf('istock/pdf.html', context)
        response = HttpResponse(doc, content_type = 'application/pdf')
        return response

@login_required
def export_csv(request):
    sales_data = salesResource()
    dataset = sales_data.export()
    response = HttpResponse(dataset.csv, content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="Sales.csv"'
    return response

@login_required
def export_excel(request):
    sales_data = salesResource()
    dataset = sales_data.export()
    response = HttpResponse(dataset.xls, content_type = 'application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sales.xls"'
    return response

@login_required
def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sales.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sales')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Product Name', 'Quantity', 'Date of Sale', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = sales.objects.all().values_list('sales_name', 'quantity', 'date_of_sale')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
