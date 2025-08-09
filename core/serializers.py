from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author, Category, Book, Borrow, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
   
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)
        return user
   

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'author', 'author_name', 
                  'category', 'category_name', 'total_copies', 'available_copies']


class BorrowSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True)

    class Meta:
        model = Borrow
        fields = ['id', 'user', 'book', 'book_id', 'borrow_date', 'due_date', 'return_date']
        read_only_fields = ['user', 'borrow_date', 'due_date', 'return_date']


class ReturnBookSerializer(serializers.Serializer):
    borrow_id = serializers.IntegerField()
