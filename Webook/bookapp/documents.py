from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry
from .models import Book

@registry.register_document
class BookDocument(Document):
    id = fields.KeywordField()
    name = fields.TextField()
    summary = fields.TextField()
    date_of_publication = fields.DateField()
    number_of_sales = fields.IntegerField()
    author = fields.KeywordField()

    class Index:
        name = 'books'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Book

    def prepare_author(self, instance):
        return str(instance.author)  # Convert UUID to string