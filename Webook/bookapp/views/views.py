from django.shortcuts import render, HttpResponse
from django_opensearch_dsl.search import Search
from django.core.paginator import Paginator
from bookapp.models import Book, Author
from ..documents import BookDocument

using_django_opensearch_dsl = True #SE CAMBIA DE VALOR SI NO SE QUIERE USAR OPENSEARCH
# Create your views here.
def home(request):
    return render(request, "home.html")

def book_search(request):

    query = request.GET.get('q')
    if query:
        
        if using_django_opensearch_dsl:
            book_document = BookDocument.search().query("match", summary=query)
            # Usa 'meta.id' para obtener el ID de cada documento
            book_list = [{'id': hit.meta.id, 'name': hit.name, 'summary': hit.summary, 'date_of_publication': hit.date_of_publication, 'number_of_sales': hit.number_of_sales, 'author': hit.author} for hit in book_document]
            print(book_list)
        else:
            books = Book.objects.all()
            book_list = [book for book in books if query.lower() in book.summary.lower()]
         
    else:
        if using_django_opensearch_dsl:
            print("AQUI ESTOY")
            search = Search(index='books')
            response = search.execute()
            book_list = [{'id': hit.meta.id, 'name': hit.name, 'summary': hit.summary, 'date_of_publication': hit.date_of_publication, 'number_of_sales': hit.number_of_sales, 'author': hit.author} for hit in response]
            print(book_list)
        else:
            book_list = Book.objects.all()

    authors = Author.objects.all()
    authors_dict = {author.id: author.name for author in authors}
    paginator = Paginator(book_list, 10)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book_templates/book_search_results.html', {'page_obj': page_obj, 'query': query, 'authors_dict': authors_dict, 'using_django_opensearch_dsl': using_django_opensearch_dsl})