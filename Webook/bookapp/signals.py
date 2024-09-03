from django.db.models.signals import post_save, post_delete # type: ignore
from django.dispatch import receiver # type: ignore
from django.core.cache import cache # type: ignore
from .models import Book, Sales, Author, Review
from .cache import is_cache_active

# Author's views
@receiver([post_save, post_delete], sender=Author)
def purge_author_list_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('author_list')

@receiver([post_save, post_delete], sender=Author)
@receiver([post_save, post_delete], sender=Book)
@receiver([post_save, post_delete], sender=Review)
@receiver([post_save, post_delete], sender=Sales)
def purge_author_statistics_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('author_statistics')


# Book's views


@receiver([post_save, post_delete], sender=Book)
@receiver([post_save, post_delete], sender=Author)
def purge_book_list_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('book_list')
        cache.delete('author_list_for_books')


@receiver([post_save, post_delete], sender=Book)
@receiver([post_save, post_delete], sender=Review)
def purge_top_rated_books_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('top_rated_books')


@receiver([post_save, post_delete], sender=Sales)
@receiver([post_save, post_delete], sender=Book)
def purge_total_sales_cache(sender, instance, **kwargs):
    if isinstance(instance, Sales):
        cache.delete(f'total_sales_{instance.book.id}')
        cache.delete(f'total_sales_author_{instance.book.author.id}')
    elif isinstance(instance, Book):
        cache.delete(f'total_sales_{instance.id}')
        cache.delete(f'total_sales_author_{instance.author.id}')


@receiver([post_save, post_delete], sender=Review)
def purge_average_score_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache_key = f'average_score_{instance.book.id}'
        cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Book)
@receiver([post_save, post_delete], sender=Sales)
@receiver([post_save, post_delete], sender=Author)
def purge_top_selling_books_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('top_selling_books')


# Review's views

@receiver([post_save, post_delete], sender=Review)
@receiver([post_save, post_delete], sender=Book)
def purge_review_list_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('review_list')
        cache.delete('book_list_for_reviews')



# Sales's views

@receiver([post_save, post_delete], sender=Sales)
@receiver([post_save, post_delete], sender=Book)
def purge_sales_list_cache(sender, instance, **kwargs):
    if is_cache_active():
        cache.delete('sales_list')
        cache.delete('book_list_for_sales')
