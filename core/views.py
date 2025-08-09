from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import date, timedelta
from django.contrib.auth.models import User
from .models import Author, Category, Book, Borrow
from .serializers import (
    RegisterSerializer, AuthorSerializer, CategorySerializer,
    BookSerializer, BorrowSerializer, ReturnBookSerializer,
    UserProfileSerializer
)


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorListCreateAPIView(APIView):
    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can create authors."}, status=status.HTTP_403_FORBIDDEN)
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can create categories."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListCreateAPIView(APIView):
    def get(self, request):
        books = Book.objects.all()
        author = request.GET.get('author')
        category = request.GET.get('category')
        if author:
            books = books.filter(author__id=author)
        if category:
            books = books.filter(category__id=category)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can add books."}, status=status.HTTP_403_FORBIDDEN)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailAPIView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can update books."}, status=status.HTTP_403_FORBIDDEN)
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Only admins can delete books."}, status=status.HTTP_403_FORBIDDEN)
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response({"detail": "Book deleted successfully."}, status=status.HTTP_200_OK)


class BorrowBookAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        active_borrows = Borrow.objects.filter(user=user, return_date__isnull=True)

        if active_borrows.count() >= 3:
            return Response({"error": "You have reached your borrowing limit (3 books)."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = BorrowSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.validated_data['book']
            if book.available_copies <= 0:
                return Response({"error": "No available copies for this book."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                book.available_copies -= 1
                book.save()

                borrow = Borrow.objects.create(
                    user=user,
                    book=book,
                    due_date=date.today() + timedelta(days=14)
                )

                return Response(BorrowSerializer(borrow).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActiveBorrowsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        borrows = Borrow.objects.filter(user=request.user, return_date__isnull=True)
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)


class ReturnBookAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReturnBookSerializer(data=request.data)
        if serializer.is_valid():
            borrow_id = serializer.validated_data['borrow_id']
            borrow = get_object_or_404(Borrow, id=borrow_id, user=request.user)

            if borrow.return_date:
                return Response({"error": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                borrow.return_date = date.today()
                borrow.save()

                book = borrow.book
                book.available_copies += 1
                book.save()

                if borrow.return_date > borrow.due_date:
                    days_late = (borrow.return_date - borrow.due_date).days
                    profile = borrow.user.profile
                    profile.penalty_points += days_late
                    profile.save()

                return Response({"message": "Book returned successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPenaltyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user != user and not request.user.is_staff:
            return Response({"error": "You are not authorized to view this information."}, status=status.HTTP_403_FORBIDDEN)
        profile = user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
