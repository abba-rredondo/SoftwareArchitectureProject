from django.shortcuts import render, redirect
from ..models import Book, Author
from ..forms import BookForm
from cassandra.cqlengine.query import DoesNotExist
from django.contrib import messages


def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_templates/book_list.html', {'books': books})


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
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
