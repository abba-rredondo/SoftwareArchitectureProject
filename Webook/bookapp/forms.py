from django import forms
from .models import Author, Book, Review, Sales
from cassandra.cqlengine.query import DoesNotExist
from django.forms.widgets import DateInput
from django.conf import settings
import uuid
import os

class AuthorForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )
    image = forms.ImageField(required=False)  # Campo de imagen

    class Meta:
        model = Author
        fields = ['name', 'date_of_birth', 'country_of_origin', 'description', 'image']

    def save(self, *args, **kwargs):
        instance = super(AuthorForm, self).save(commit=False)

       
        if not instance.id:
            instance.id = uuid.uuid4()  

        
        if self.cleaned_data.get('image'):
            image = self.cleaned_data['image']
            image_path = f'author_images/{image.name}'
            
            
            if instance.image_path:
                old_image_path = os.path.join(settings.MEDIA_ROOT, instance.image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            
            with open(f'{settings.MEDIA_ROOT}/{image_path}', 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            instance.image_path = image_path
        
        
        instance.save()
        return instance
    

class DateInput(forms.DateInput):
    input_type = 'date'  # Widget personalizado para la fecha de publicación

class BookForm(forms.ModelForm):
    author = forms.ChoiceField(choices=[])  # Campo de elección de autor
    date_of_publication = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),  # Widget de selección de fecha
        required=False
    )
    number_of_sales = forms.IntegerField(min_value=0, required=False)  # Campo de ventas
    cover_image = forms.ImageField(required=False)  # Campo de imagen para la portada

    class Meta:
        model = Book
        fields = ['name', 'summary', 'date_of_publication', 'number_of_sales', 'author', 'cover_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar dinámicamente las opciones del campo 'author' desde la base de datos
        try:
            authors = Author.objects.all()
            author_choices = [(author.id, author.name) for author in authors]
        except Author.DoesNotExist:
            author_choices = []
        self.fields['author'].choices = author_choices

    def save(self, *args, **kwargs):
        instance = super(BookForm, self).save(commit=False)

        # Generar un UUID si el libro es nuevo (no tiene ID)
        if not instance.id:
            instance.id = uuid.uuid4()  # Genera un nuevo UUID si no existe

        # Verificar si se ha subido una nueva imagen de portada
        if self.cleaned_data.get('cover_image'):
            image = self.cleaned_data['cover_image']
            image_path = f'book_covers/{image.name}'

            # Eliminar la portada anterior si existe
            if instance.cover_image_path:
                old_image_path = os.path.join(settings.MEDIA_ROOT, instance.cover_image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Guardar la nueva imagen
            with open(f'{settings.MEDIA_ROOT}/{image_path}', 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            instance.cover_image_path = image_path

        # Guardar el libro
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
