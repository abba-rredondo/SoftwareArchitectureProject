from django.shortcuts import render, redirect # type: ignore
from ..models import Review, Book
from ..forms import ReviewForm
from django.contrib import messages # type: ignore
from uuid import uuid4
from django.core.paginator import Paginator # type: ignore
from django.core.cache import cache # type: ignore
from django.db import models # type: ignore
from ..cache import is_cache_active


def review_list(request):
    cache_key_reviews = 'review_list'
    cache_key_books = 'book_list_for_reviews'

    reviews = None
    books = None

    if is_cache_active():
        reviews = cache.get(cache_key_reviews)
        books = cache.get(cache_key_books)

    if reviews is None:
        reviews_queryset = Review.objects.all()
        reviews = [{'id': str(review.id), 'score': review.score, 'review_text': review.review_text, 'up_votes': review.up_votes, 'book_id': str(review.book)} for review in reviews_queryset]
        if is_cache_active():
            cache.set(cache_key_reviews, reviews, timeout=600)

    if books is None:
        books_queryset = Book.objects.all()
        books = [{'id': str(book.id), 'name': book.name, 'author_id': str(book.author)} for book in books_queryset]
        if is_cache_active():
            cache.set(cache_key_books, books, timeout=600)

    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'review_templates/review_list.html', {'page_obj': page_obj, 'books': books})

def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review_instance = form.save(commit=False)
            if not review_instance.id:
                review_instance.id = uuid4()
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'review_templates/review_form.html', {'form': form})

def review_update(request, pk):

    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        messages.error(request, 'Review not found')
        redirect("/")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_templates/review_form.html', {'form': form})

def review_delete(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        messages.error(request, 'Review not found')
        redirect("/")

    if request.method == 'POST':
        review.delete()
        return redirect('review_list')
    return render(request, 'review_templates/review_confirm_delete.html', {'review': review})

