from django.shortcuts import render, redirect
from ..models import Book, Author, Review, Sales
from ..forms import BookForm
from cassandra.cqlengine.query import DoesNotExist
from django.contrib import messages
from uuid import uuid4
from cassandra.cluster import Cluster
from django.db.models import Avg
from cassandra.cqlengine import columns
from datetime import datetime
from django.core.paginator import Paginator

def book_list(request):
    book_list = Book.objects.all()
    paginator = Paginator(book_list, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    authors = Author.objects.all()
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

def get_total_sales(book_id):
    sales_records = Sales.objects.filter(book=book_id)
    total_sales = sum(sale.sales for sale in sales_records)
    return total_sales

def get_total_sales_author(author_id):
    # Obtener todos los libros del autor y asegurarse de que sea una lista
    books = list(Book.objects.filter(author=author_id).values_list('id', flat=True))

    # Verificar si la lista de libros está vacía
    if not books:
        return 0

    # Filtrar las ventas por esos libros y calcular el total
    sales_records = Sales.objects.filter(book__in=books)
    total_sales = sum(sale.sales for sale in sales_records)
    return total_sales




def get_average_score(book_id):
    reviews = Review.objects.filter(book=book_id)
    if reviews.count() == 0:
        return 0
    total_score = sum(review.score for review in reviews)
    average_score = total_score / reviews.count()
    return average_score

def top_selling_books(request):
    top_books = Book.objects.all().order_by('-number_of_sales')[:50]
    
    data = []
    for book in top_books:
        total_sales = get_total_sales(book.id)
        author_sales = get_total_sales_author(book.author) 
        average_score = get_average_score(book.id)
        
        # Verificar si el libro fue uno de los 5 más vendidos en el año de su publicación
        publication_year = book.date_of_publication
        if publication_year:
            # Convertir a un objeto datetime y extraer el año
            publication_year = datetime.strptime(str(publication_year), '%Y-%m-%d').year
        else:
            publication_year = None
        
        top_books_year = Sales.objects.filter(year=publication_year).order_by('-sales')[:5]
        print(top_books_year)
        was_top_5 = any(sale.book == book.id for sale in top_books_year)
        
        data.append({
            'book': book.name,
            'total_sales': total_sales,
            'author_sales': author_sales,
            'average_score': average_score,
            'was_top_5': was_top_5
        })
    
    return render(request, 'book_templates/top_selling_books.html', {'data': data})