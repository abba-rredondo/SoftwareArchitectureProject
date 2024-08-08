from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator
from bookapp.models import Book

# Create your views here.
def home(request):
    return render(request, "home.html")

def book_search(request):
    query = request.GET.get('q')
    if query:
        
        books = Book.objects.all()
        book_list = [book for book in books if query.lower() in book.summary.lower()]
    else:
        book_list = Book.objects.all()

    paginator = Paginator(book_list, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book_templates/book_search_results.html', {'page_obj': page_obj, 'query': query})