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

    sales_data = []
    for sale in page_obj:
        sales_data.append({
            'book': book_dict.get(sale.book, 'Unknown Book'),
            'year': sale.year,
            'sales': sale.sales,
            'id': sale.book
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

