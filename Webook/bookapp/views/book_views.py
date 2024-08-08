from django.shortcuts import render, redirect
from ..models import Book, Author, Review, Sales
from ..forms import BookForm
from cassandra.cqlengine.query import DoesNotExist
from django.contrib import messages
from uuid import uuid4
from cassandra.cluster import Cluster
from django.db.models import Avg


def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_templates/book_list.html', {'books': books})


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book_instance = form.save(commit=False)
            if not book_instance.id:
                book_instance.id = uuid4()  
            book_instance.save()
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'book_templates/book_form.html', {'form': form})


def book_update(request, pk):
    try:
        book = Book.objects.get(id=pk)
    except Book.DoesNotExist:
        messages.error(request, 'Book not found')
        redirect("/")

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_templates/book_form.html', {'form': form})


def book_delete(request, pk):
    try:
        book = Book.objects.get(id=pk)
    except Book.DoesNotExist:
        messages.error(request, 'Book not found')
        redirect("/")
    
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_templates/book_confirm_delete.html', {'book': book})



def top_rated_books(request):
    # Paso 1: Calcular el puntaje promedio para cada libro
    books = Book.objects.all()
    book_scores = []

    for book in books:
        # Obtener reseñas del libro
        reviews = Review.objects.filter(book=book.id)
        total_score = 0
        # Calcular el puntaje promedio
        for review in reviews:
            total_score += review.score
        
        review_count = reviews.count()
        average_score = total_score / review_count if review_count > 0 else 0

        book_scores.append({
            'book': book,
            'average_score': average_score
        })
    print('llegoooo aquiiiiiiiii')
    top_books = sorted(book_scores, key=lambda x: x['average_score'], reverse=True)[:10]
    print(top_books)
    result = []

    for item in top_books:
        book = item['book']
        average_score = item['average_score']


        reviews = Review.objects.filter(book=book.id)
        

        highest_review = max(reviews, key=lambda r: r.score, default=None)
        lowest_review = min(reviews, key=lambda r: r.score, default=None)
        most_popular_review = max(reviews, key=lambda r: r.up_votes, default=None)

        result.append({
            'book': book,
            'average_score': average_score,
            'highest_review': highest_review,
            'lowest_review': lowest_review,
            'most_popular_review': most_popular_review
        })

    return render(request, 'book_templates/top_rated_books.html', {'books': result})
