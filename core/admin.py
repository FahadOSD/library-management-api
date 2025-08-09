from django.contrib import admin
from .models import UserProfile, Author, Category, Book, Borrow

admin.site.register(UserProfile)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Borrow)