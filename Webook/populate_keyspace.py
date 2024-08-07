import requests
import random
import uuid
from datetime import datetime, timedelta
from cassandra.cluster import Cluster
from faker import Faker


# Conectar a la base de datos Cassandra
print('Conectando a la base de datos Cassandra...')
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('tu_keyspace')
faker = Faker()
print('Conexión exitosa')

# Función para obtener datos de la API de Open Library
def fetch_author(author_key):
    url = f'https://openlibrary.org/authors/{author_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['name']
        except:
            return faker.name()
    

def fetch_author_birth(author_key):
    url = f'https://openlibrary.org/authors/{author_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['birth_date']
        except:
            return faker.date_of_birth()

def fetch_author_places(author_key):
    url = f'https://openlibrary.org/authors/{author_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['subject_places']
        except:
            return faker.country()           

def fetch_author_description(author_key):
    url = f'https://openlibrary.org/authors/{author_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['bio']['value']
        except:
            return faker.text()

def fetch_books_by_author(author_key):
    url = f'https://openlibrary.org/authors/{author_key}/works.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['entries']
    return []


def fetch_book_title(book_key):
    url = f'https://openlibrary.org/works/{book_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['title']
        except:
            return faker.sentence()

def fetch_book_description(book_key):
    url = f'https://openlibrary.org/works/{book_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['description']['value']
        except:
            return faker.text()
        
def fetch_book_date_of_publication(book_key):
    url = f'https://openlibrary.org/works/{book_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['first_publish_date']
        except:
            return faker.date()

def fetch_book_title(book_key):
    url = f'https://openlibrary.org/works/{book_key}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['title']
        except:
            return faker.sentence()


# Insertar datos en Cassandra

def insert_data():
    # Obtener 50 autores
    authors = []
    for i in range(1, 51):
        author_key = f'OL{i}A'
        author_name = fetch_author(author_key)
        if author_name:
            author_id = uuid.uuid4()
            author_birth = fetch_author_birth(author_key)
            author_country = fetch_author_places(author_key)
            author_description = fetch_author_description(author_key)
            authors.append((author_key, author_name, author_id))
            session.execute(
                """
                INSERT INTO author (id, name, date_of_birth, country_of_origin, description) VALUES (%s, %s, %s, %s, %s)
                """,
                (author_id, author_name, author_birth, author_country, author_description)
            )

    # Obtener 300 libros y agregar reseñas y ventas
    total_books = 0
    for author_key, author_name, author_id in authors:
        books = fetch_books_by_author(author_key)
        for book in books:
            book_key = book['key'].split('/')[-1]
            if total_books >= 300:
                break
            book_id = uuid.uuid4()
            name = fetch_book_title(book_key)
            summary = fetch_book_description(book_key)
            date_of_publication = fetch_book_date_of_publication(book_key)
            number_of_sales = random.randint(1000, 10000)
            session.execute(
                """
                INSERT INTO book (id, name, author, number_of_sales, date_of_publication, summary) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (book_id, name, author_id, number_of_sales, date_of_publication, summary)
            )
            total_books += 1

            # Agregar entre 1 y 10 reseñas por libro
            num_reviews = random.randint(2, 10)
            for _ in range(num_reviews):
                review_id = uuid.uuid4()
                review_text = faker.text()
                score = random.randint(1, 5)
                up_votes = random.randint(0, 1000)
                session.execute(
                    """
                    INSERT INTO review (id, book, review_text, score, up_votes) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (review_id, book_id, review_text, score, up_votes)
                )

            # Agregar al menos 5 años de ventas por libro
            for year in range(datetime.now().year - 7, datetime.now().year):
                sales = random.randint(100, 1000)
                session.execute(
                    """
                    INSERT INTO sales (book, year, sales) VALUES (%s, %s, %s)
                    """,
                    (book_id, year, sales)
                )


if __name__ == '__main__':
   insert_data()
   print('Datos insertados correctamente')
