from django.shortcuts import render, get_object_or_404, redirect
from ..models import Sales, Book
from ..forms import SalesForm
from django.contrib import messages
from django.core.paginator import Paginator

def sales_list(request):
    sales = Sales.objects.all().order_by('book', 'year')
    books = Book.objects.all()

    paginator = Paginator(sales, 70)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    
    book_dict = {book.id: book.name for book in books}

    
    sales_by_book = {}
    for sale in page_obj:
        book_id = sale.book  
        if book_id not in sales_by_book:
            sales_by_book[book_id] = {
                'name': book_dict.get(book_id, 'Unknown Book'),
                'sales': {year: '-' for year in range(2017, 2024)}
            }
        sales_by_book[book_id]['sales'][sale.year] = sale.sales

    return render(request, 'sales_templates/sales_list.html', {
        'page_obj': page_obj,
        'sales_by_book': sales_by_book
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

