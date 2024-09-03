from django.conf import settings # type: ignore

def is_cache_active():
    cache_backend = settings.CACHES.get('default', {}).get('BACKEND')
    return 'redis' in cache_backend.lower() if cache_backend else False
