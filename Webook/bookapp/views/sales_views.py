from django.shortcuts import render, get_object_or_404, redirect
from ..models import Sales, Book
from ..forms import SalesForm
from django.contrib import messages

def sales_list(request):
    sales = Sales.objects.all()
    books = Book.objects.all()
    return render(request, 'sales_templates/sales_list.html', {'sales': sales, 'books': books})

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
