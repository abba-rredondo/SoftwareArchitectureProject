from django import forms
from .models import Author, Book, Review, Sales
from cassandra.cqlengine.query import DoesNotExist

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'date_of_birth', 'country_of_origin', 'description']


class BookForm(forms.ModelForm):
    author = forms.ChoiceField(choices=[])

    class Meta:
        model = Book
        fields = ['name', 'summary', 'date_of_publication', 'number_of_sales', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            authors = Author.objects.all()
            author_choices = [(author.id, author.name) for author in authors]
        except DoesNotExist:
            author_choices = []
        self.fields['author'].choices = author_choices

class ReviewForm(forms.ModelForm):
    book = forms.ChoiceField(choices=[])

    class Meta:
        model = Review
        fields = ['book', 'review_text', 'score', 'up_votes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            books = Book.objects.all()
            book_choices = [(book.id, book.name) for book in books]
        except DoesNotExist:
            book_choices = []
        self.fields['book'].choices = book_choices


class SalesForm(forms.ModelForm):
    book = forms.ChoiceField(choices=[])

    class Meta:
        model = Sales
        fields = ['book', 'year', 'sales']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            books = Book.objects.all()
            book_choices = [(book.id, book.name) for book in books]
        except DoesNotExist:
            book_choices = []
        self.fields['book'].choices = book_choices
