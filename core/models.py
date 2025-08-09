from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    penalty_points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Name: {self.user.username}"


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    
    def __str__(self):
        return f"Author name: {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return f"Category: {self.name}"


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    
    def __str__(self):
        return f"Book title: {self.title}"


class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
