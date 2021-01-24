from django.db import models

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your models here.
class products(models.Model):
    code = models.CharField(max_length = 10, unique = True)
    product_name = models.CharField(max_length = 200 )
    quantity = models.PositiveIntegerField(default = 0)
    buying_price_per_each = models.FloatField(default = 0)
    selling_price_per_each = models.FloatField(default = 0)


    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.product_name



class sales(models.Model):
    seller = models.ForeignKey(User, on_delete = models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add = True, null=True)
    transaction_id = models.CharField(max_length = 200, null = True, blank = True)
    ordered = models.BooleanField(default = False, null = True)
    customer_name = models.CharField(max_length = 200, null = True, blank = True)
    postal_address = models.CharField(max_length = 200, null = True, blank = True)
    physical_address = models.CharField(max_length = 200, null = True, blank = True)
    customer_TIN = models.CharField(max_length = 200, null = True, blank = True)
    customer_VRN = models.CharField(max_length = 200, null = True, blank = True)
    profoma = models.BooleanField(default = False, null = True)

    class Meta:
        verbose_name_plural = 'Sales'

    def __str__(self):
        return str(self.id)

    @property
    def profit(self):
        profit = get_total_amount - total_buying_price
        return profit


    @property
    def get_total_amount(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.totalAmount for item in orderitems])
        return total

    @property
    def getVAT(self):
        VAT = (18/100) * self.get_total_amount
        return VAT
        total = self.get_total_amount
        vat = (18/100) * total
        return vat

    @property
    def total_buying_price(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.buying_price*item.quantity for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def order(self):
        orderitems = self.orderitem_set.all()
        return orderitems


class OrderItem(models.Model):
    product = models.ForeignKey(products, on_delete = models.SET_NULL, null = True, blank = True)
    sale = models.ForeignKey(sales, on_delete = models.SET_NULL, null = True, blank = True)
    quantity = models.PositiveIntegerField(default = 0, null = True, blank = True)
    date_added = models.DateTimeField(auto_now_add = True)
    price = models.FloatField(null = True, blank = True)
    buying_price = models.FloatField(null = True, blank = True)
    product_name = models.CharField(max_length = 200, null = True, blank = True)

    def __str__(self):
        return str(self.id)

    @property
    def totalAmount(self):
        total = self.quantity * self.price
        return total



class Purchase(models.Model):
    # The product foreign key is needed
    product = models.ForeignKey(products, related_name = 'product', null = True, blank = True, on_delete = models.CASCADE)
    product_name = models.CharField(max_length = 200)
    quantity = models.PositiveIntegerField(default = 0)
    quantity_before = models.PositiveIntegerField(default = 0)
    quantity_after = models.PositiveIntegerField(default = 0)
    total_price = models.PositiveIntegerField(default = 0)
    date = models.DateField()

    class Meta:
        verbose_name_plural = 'Purchases'

    def __str__(self):
        return self.product.product_name


class Deposit(models.Model):
    first_date = models.DateField()
    last_date = models.DateField()
    deposition_date = models.DateField()
    amount = models.FloatField()
    bank = models.CharField(max_length=50)
    deposited_by = models.ForeignKey(User, on_delete = models.PROTECT, null=True, blank=True)


    class Meta:
        verbose_name_plural = 'Deposits'

    def __str__(self):
        start_date = str(self.first_date)
        last_date = str(self.last_date)
        return "From " + start_date + " to " + last_date


EXPENSE_CHOICES = (
    ('Electricity', 'Electricity'),
    ('Meal', 'Meal'),
    ('Rent', 'Rent'),
    ('Security', 'Security'),
    ('Others', 'Others'),
)

class Expenses(models.Model):
    expense = models.CharField(choices = EXPENSE_CHOICES, max_length = 100)
    description = models.CharField(max_length = 100, null = True, blank = True)
    date = models.DateField()
    amount = models.FloatField()

    class Meta:
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return str(self.date)


class Percentages(models.Model):
    name = models.CharField(max_length = 50)
    percent = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = 'Percentages'

    def __str__(self):
        return self.name
