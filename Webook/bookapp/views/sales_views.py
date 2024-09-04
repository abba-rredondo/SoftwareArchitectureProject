from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from ..models import Sales, Book
from ..forms import SalesForm
from django.contrib import messages # type: ignore
from django.core.paginator import Paginator # type: ignore
from ..cache import is_cache_active
from django.core.cache import cache # type: ignore

def sales_list(request):
    cache_key_sales = 'sales_list'
    cache_key_books = 'book_list_for_sales'

    sales = None
    books = None

    if is_cache_active():
        sales = cache.get(cache_key_sales)
        books = cache.get(cache_key_books)

    if sales is None:
        sales_queryset = Sales.objects.all().order_by('book', 'year')
        sales = [{'book': str(sale.book), 'year': sale.year, 'sales': sale.sales, 'id': str(sale.book)} for sale in sales_queryset]
        if is_cache_active():
            cache.set(cache_key_sales, sales, timeout=600)

    if books is None:
        books_queryset = Book.objects.all()
        books = [{'id': str(book.id), 'name': book.name} for book in books_queryset]
        if is_cache_active():
            cache.set(cache_key_books, books, timeout=600)

    paginator = Paginator(sales, 70)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    book_dict = {book['id']: book['name'] for book in books}

    sales_data = []
    for sale in page_obj:
        sales_data.append({
            'book': book_dict.get(sale['book'], 'Unknown Book'),
            'year': sale['year'],
            'sales': sale['sales'],
            'id': sale['book']
        })

    return render(request, 'sales_templates/sales_list.html', {
        'page_obj': page_obj,
        'sales_data': sales_data
    })


def sales_create(request):
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_list') 
    else:
        form = SalesForm()

    return render(request, 'sales_templates/sales_form.html', {'form': form})

def sales_update(request, book_id, year):
 
    try:
        sales = Sales.objects.get(book=book_id, year=year)
    except Sales.DoesNotExist:
        messages.error(request, 'Sales not found')
        redirect("/")

    if request.method == 'POST':
        form = SalesForm(request.POST, instance=sales)
        if form.is_valid():
            form.save()
            return redirect('sales_list')
    else:
        form = SalesForm(instance=sales)
    return render(request, 'sales_templates/sales_form.html', {'form': form})

def sales_delete(request, book_id, year):

    try:
        sales = Sales.objects.get(book=book_id, year=year)
    except Sales.DoesNotExist:
        messages.error(request, 'Sales not found')
        redirect("/")

    if request.method == 'POST':
        sales.delete()
        return redirect('sales_list')
    return render(request, 'sales_templates/sales_confirm_delete.html', {'sales': sales})

