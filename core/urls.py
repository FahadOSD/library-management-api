from django.urls import path
from .views import (
    RegisterAPIView, AuthorListCreateAPIView, CategoryListCreateAPIView,
    BookListCreateAPIView, BookDetailAPIView, BorrowBookAPIView,
    ActiveBorrowsAPIView, ReturnBookAPIView, UserPenaltyAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('authors/', AuthorListCreateAPIView.as_view(), name='authors'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='categories'),
    path('books/', BookListCreateAPIView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('borrow/', BorrowBookAPIView.as_view(), name='borrow-book'),
    path('borrow/active/', ActiveBorrowsAPIView.as_view(), name='active-borrows'),
    path('return/', ReturnBookAPIView.as_view(), name='return-book'),
    path('users/<int:user_id>/penalties/', UserPenaltyAPIView.as_view(), name='user-penalties'),
]
