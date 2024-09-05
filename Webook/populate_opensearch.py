import os
import django
import sys
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from django.conf import settings
from opensearchpy import OpenSearch, helpers
from datetime import date, datetime

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Webook.settings")
django.setup()

from bookapp.documents import BookDocument
from bookapp.models import Author

# Cassandra connection
cluster = Cluster(['cassandra'])
session = cluster.connect('tu_keyspace')
session.row_factory = dict_factory

# OpenSearch connection
opensearch_config = settings.OPENSEARCH_DSL['default']
client = OpenSearch(
    hosts=opensearch_config['hosts'],
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False,
)

def fetch_books_from_cassandra():
    query = "SELECT * FROM book"
    return session.execute(query)

def get_author_name(author_id):
    try:
        author = Author.objects.get(id=author_id)
        return author.name
    except Author.DoesNotExist:
        return "Unknown Author"

def format_date(date_obj): #En caso de usar arreglar
    if isinstance(date_obj, str):
        try:
            # Intentar analizar la cadena en el formato esperado
            parsed_date = datetime.strptime(date_obj, "%Y-%m-%d").date()
            return parsed_date.isoformat()
        except ValueError:
            print(f"Error parsing date string: {date_obj}")
            return None
    elif isinstance(date_obj, date):
        return date_obj.isoformat()
    else:
        return None

def index_books_in_opensearch(books):
    actions = []
    for book in books:
        author_name = get_author_name(book['author'])
        doc = {
            '_index': BookDocument._index._name,
            '_id': str(book['id']),
            '_source': {
                'name': book['name'],
                'summary': book['summary'],
                'date_of_publication': format_date(book['date_of_publication']),
                'number_of_sales': book['number_of_sales'],
                'author': author_name
            }
        }
        actions.append(doc)

    if actions:
        helpers.bulk(client, actions)

def main():
    print("Fetching books from Cassandra...")
    books = fetch_books_from_cassandra()
    
    print("Indexing books in OpenSearch...")
    index_books_in_opensearch(books)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()