from django.contrib import admin
from .models import Book, OrderItem, Order , BookImage

admin.site.register(Book)
admin.site.register(Order)
admin.site.register(BookImage)
admin.site.register(OrderItem)


