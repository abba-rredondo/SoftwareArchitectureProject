from django_cassandra_engine.models import DjangoCassandraModel # type: ignore
from cassandra.cqlengine import columns # type: ignore


class Author(DjangoCassandraModel):
    id = columns.UUID(primary_key=True)
    name = columns.Text(required=True, index=True)
    date_of_birth = columns.Date()
    country_of_origin = columns.Text()
    description = columns.Text()

class Book(DjangoCassandraModel):
    id = columns.UUID(primary_key=True)
    name = columns.Text(required=True, index=True)
    summary = columns.Text()
    date_of_publication = columns.Date()
    number_of_sales = columns.BigInt(default=0)
    author = columns.UUID()  # Referencia al ID del autor

class Review(DjangoCassandraModel):
    id = columns.UUID(primary_key=True)
    book = columns.UUID()  # Referencia al ID del libro
    review_text = columns.Text()
    score = columns.Integer()
    up_votes = columns.Integer(default=0)

    class Meta:
        get_pk_field = 'id'

class Sales(DjangoCassandraModel):
    book = columns.UUID(primary_key=True)
    year = columns.Integer(primary_key=True)
    sales = columns.BigInt(default=0)

    class Meta:
        get_pk_field = 'book' #book es la clave primaria de la tabla
