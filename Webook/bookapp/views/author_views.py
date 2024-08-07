from django.shortcuts import render, redirect, get_object_or_404
from ..models import Author, Book, Review, Sales
from django.db.models import Avg, Sum
from ..forms import AuthorForm
from uuid import uuid4
from django.contrib import messages


def author_list(request):
    authors = Author.objects.all()
    return render(request, 'author_templates/author_list.html', {'authors': authors})


def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.id = uuid4()  
            author.save()
            return redirect('author_list')
    else:
        form = AuthorForm()
    return render(request, 'author_templates/author_form.html', {'form': form})


def author_update(request, pk):

    try:
        author = Author.objects.get(id=pk)
    except Author.DoesNotExist:
        messages.error(request, 'Author not found')
        redirect("/")

    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'author_templates/author_form.html', {'form': form})


def author_delete(request, pk):
    try:
        author = Author.objects.get(id=pk)
    except Author.DoesNotExist:
        messages.error(request, 'Author not found')
        redirect("/")

    if request.method == 'POST':
        author.delete()
        return redirect('author_list')
    return render(request, 'author_templates/author_confirm_delete.html', {'author': author})




def author_statistics(request):
    authors = Author.objects.all()

    # Recopilando datos de los autores
    data = []
    for author in authors:
        books = Book.objects.filter(author=author.id)
        all_reviews = []
        total_sales = 0
    
        # Iterar sobre cada libro y recolectar reseñas
        for book in books:
            reviews = Review.objects.filter(book=book.id)
            all_reviews.extend(reviews)

        for book in books:
            sales_records = Sales.objects.filter(book=book.id)
            total_sales = sum(sales_record.sales for sales_record in sales_records)
             

        num_books = books.count()
        scores = [review.score for review in all_reviews]
        average_score = sum(scores) / len(scores) if scores else 0
        
        
        data.append({
            'name': author.name,
            'num_libros': num_books,
            'promedio_puntuacion': average_score,
            'ventas_totales': total_sales
        })
    
    # Ordenación y filtrado
    sort = request.GET.get('sort', 'name')
    filter_name = request.GET.get('filter_name', '')
    
    if filter_name:
        data = [d for d in data if filter_name.lower() in d['name'].lower()]
    
    if sort:
        data = sorted(data, key=lambda x: x[sort])

    return render(request, 'author_templates/author_statistics.html', {'data': data, 'sort': sort, 'filter_name': filter_name})