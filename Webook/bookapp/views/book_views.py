from django.shortcuts import render, redirect # type: ignore
from ..models import Book, Author, Review, Sales
from ..forms import BookForm
from cassandra.cqlengine.query import DoesNotExist # type: ignore
from django.contrib import messages # type: ignore
from uuid import uuid4
from cassandra.cluster import Cluster # type: ignore
from django.db.models import Avg # type: ignore
from cassandra.cqlengine import columns # type: ignore
from datetime import datetime
from django.core.paginator import Paginator # type: ignore
from django.core.cache import cache # type: ignore
from ..cache import is_cache_active

def book_list(request):
    cache_key_books = 'book_list'
    cache_key_authors = 'author_list_for_books'

    books = None
    authors = None

    if is_cache_active():
        books = cache.get(cache_key_books)
        authors = cache.get(cache_key_authors)

    if books is None:
        books_queryset = Book.objects.all()
        books = [{'id': str(book.id), 'name': book.name, 'author_id': str(book.author)} for book in books_queryset] 
        if is_cache_active():
            cache.set(cache_key_books, books, timeout=600)

    if authors is None:
        authors_queryset = Author.objects.all()
        authors = [{'id': str(author.id), 'name': author.name} for author in authors_queryset]  
        if is_cache_active():
            cache.set(cache_key_authors, authors, timeout=600)

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book_templates/book_list.html', {'page_obj': page_obj, 'authors': authors})


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
    cache_key = 'top_rated_books'

    result = None

    if is_cache_active():
        result = cache.get(cache_key)

    if result is None:
        books_queryset = Book.objects.all()
        books = [{'id': str(book.id), 'name': book.name} for book in books_queryset]

        book_scores = []
        for book in books:
            reviews_queryset = Review.objects.filter(book=book['id'])
            total_score = sum(review.score for review in reviews_queryset)
            review_count = reviews_queryset.count()
            average_score = total_score / review_count if review_count > 0 else 0

            highest_review = max(reviews_queryset, key=lambda r: r.score, default=None)
            lowest_review = min(reviews_queryset, key=lambda r: r.score, default=None)
            most_popular_review = max(reviews_queryset, key=lambda r: r.up_votes, default=None)

            book_scores.append({
                'book': book,
                'average_score': average_score,
                'highest_review': {'score': highest_review.score, 'review_text': highest_review.review_text} if highest_review else None,
                'lowest_review': {'score': lowest_review.score, 'review_text': lowest_review.review_text} if lowest_review else None,
                'most_popular_review': {
                    'score': most_popular_review.score if most_popular_review else None,
                    'review_text': most_popular_review.review_text if most_popular_review else None,
                    'up_votes': most_popular_review.up_votes if most_popular_review else None
                } if most_popular_review else None
            })

        result = sorted(book_scores, key=lambda x: x['average_score'], reverse=True)[:10]

        if is_cache_active():
            cache.set(cache_key, result, timeout=600)

    return render(request, 'book_templates/top_rated_books.html', {'books': result})






def get_total_sales(book_id):
    cache_key = f'total_sales_{book_id}'
    
    if is_cache_active():
        total_sales = cache.get(cache_key)
        if total_sales is not None:
            return total_sales

    sales_records = Sales.objects.filter(book=book_id)
    total_sales = sum(sale.sales for sale in sales_records)
    
    if is_cache_active():
        cache.set(cache_key, total_sales, timeout=600)
    
    return total_sales

def get_total_sales_author(author_id):
    cache_key = f'total_sales_author_{author_id}'
    
    if is_cache_active():
        total_sales = cache.get(cache_key)
        if total_sales is not None:
            return total_sales

    books = list(Book.objects.filter(author=author_id).values_list('id', flat=True))

    if not books:
        return 0

    sales_records = Sales.objects.filter(book__in=books)
    total_sales = sum(sale.sales for sale in sales_records)
    
    if is_cache_active():
        cache.set(cache_key, total_sales, timeout=600)
    
    return total_sales



def get_average_score(book_id):
    if is_cache_active():
        cache_key = f'average_score_{book_id}'
        average_score = cache.get(cache_key)
        
        if average_score is not None:
            return average_score
    
    reviews = Review.objects.filter(book=book_id)
    if reviews.count() == 0:
        return 0
    
    total_score = sum(review.score for review in reviews)
    average_score = total_score / reviews.count()
    
    if is_cache_active():
        cache.set(cache_key, average_score, timeout=600)
    
    return average_score

def top_selling_books(request):
    cache_key = 'top_selling_books'
    
    if is_cache_active():
        data = cache.get(cache_key)
        if data is not None:
            return render(request, 'book_templates/top_selling_books.html', {'data': data})

    top_books = Book.objects.all().order_by('-number_of_sales')[:50]
    
    data = []
    for book in top_books:
        total_sales = get_total_sales(book.id)
        author_sales = get_total_sales_author(book.author)
        average_score = get_average_score(book.id)
        
        publication_year = book.date_of_publication
        if publication_year:
            publication_year = datetime.strptime(str(publication_year), '%Y-%m-%d').year
        else:
            publication_year = None
        
        top_books_year = Sales.objects.filter(year=publication_year).order_by('-sales')[:5]
        was_top_5 = any(sale.book == book.id for sale in top_books_year)
        
        data.append({
            'book': book.name,
            'total_sales': total_sales,
            'author_sales': author_sales,
            'average_score': average_score,
            'was_top_5': was_top_5
        })
    
    if is_cache_active():
        cache.set(cache_key, data, timeout=600)
    
    return render(request, 'book_templates/top_selling_books.html', {'data': data})

def book_profile(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        messages.error(request, 'Book not found')
        redirect("/")

    context = {
        'book': book
    }
    return render(request, 'book_templates/book_profile.html', context)