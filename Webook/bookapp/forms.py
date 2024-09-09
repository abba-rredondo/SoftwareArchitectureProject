from django import forms
from .models import Author, Book, Review, Sales
from cassandra.cqlengine.query import DoesNotExist
from django.forms.widgets import DateInput
from django.conf import settings
import uuid

class AuthorForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    image = forms.ImageField(required=False)  # Agregar el campo de imagen

    class Meta:
        model = Author
        fields = ['name', 'date_of_birth', 'country_of_origin', 'description', 'image']  # Incluir 'image' en los campos

    def save(self, *args, **kwargs):
        instance = super(AuthorForm, self).save(commit=False)
        
        if not instance.id:
            instance.id = uuid.uuid4()
        
        if self.cleaned_data.get('image'):
            image = self.cleaned_data['image']
            image_path = f'author_images/{image.name}'
            
            with open(f'{settings.MEDIA_ROOT}/{image_path}', 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            instance.image_path = image_path
        
        instance.save()
        return instance
    

class BookForm(forms.ModelForm):
    author = forms.ChoiceField(choices=[])
    date_of_publication = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    cover_image = forms.ImageField(required=False)  

    class Meta:
        model = Book
        fields = ['name', 'summary', 'date_of_publication', 'number_of_sales', 'author', 'cover_image']  # Incluir 'cover_image'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            authors = Author.objects.all()
            author_choices = [(author.id, author.name) for author in authors]
        except Author.DoesNotExist:
            author_choices = []
        self.fields['author'].choices = author_choices

    def save(self, *args, **kwargs):
        instance = super(BookForm, self).save(commit=False)
        if self.cleaned_data['cover_image']:          
            cover_image = self.cleaned_data['cover_image']
            cover_image_path = f'book_covers/{cover_image.name}'
            with open(f'{settings.MEDIA_ROOT}/{cover_image_path}', 'wb+') as f:
                for chunk in cover_image.chunks():
                    f.write(chunk)
            instance.cover_image_path = cover_image_path
        instance.save()
        return instance


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
