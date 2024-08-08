from django.urls import path
from .views import author_views, book_views, views, review_views, sales_views

urlpatterns = [
    path("", views.home, name="home"),
    path('authors/', author_views.author_list, name='author_list'),
    path('authors/new/', author_views.author_create, name='author_create'),
    path('authors/edit/<uuid:pk>/', author_views.author_update, name='author_update'),
    path('authors/delete/<uuid:pk>/', author_views.author_delete, name='author_delete'),
    path('authors/statistics/', author_views.author_statistics, name='author_statistics'),
    path('books/', book_views.book_list, name='book_list'),
    path('books/create/', book_views.book_create, name='book_create'),
    path('books/update/<uuid:pk>/', book_views.book_update, name='book_update'),
    path('books/delete/<uuid:pk>/', book_views.book_delete, name='book_delete'),
    path('books/top_selling', book_views.top_selling_books, name='top_selling_books'),
    path('books/top_reviews/', book_views.top_rated_books, name='top_rated_books'),
    path('reviews/', review_views.review_list, name='review_list'),
    path('reviews/create/', review_views.review_create, name='review_create'),
    path('reviews/<uuid:pk>/update/', review_views.review_update, name='review_update'),
    path('reviews/<uuid:pk>/delete/', review_views.review_delete, name='review_delete'),
    path('sales/', sales_views.sales_list, name='sales_list'),
    path('sales/create/', sales_views.sales_create, name='sales_create'),
    path('sales/<uuid:book_id>/<int:year>/update/', sales_views.sales_update, name='sales_update'),
    path('sales/<uuid:book_id>/<int:year>/delete/', sales_views.sales_delete, name='sales_delete'),

]