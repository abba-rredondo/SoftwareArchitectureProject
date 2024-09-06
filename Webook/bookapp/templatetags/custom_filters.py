from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtenido el valor del diccionario para una clave dada."""
    return dictionary.get(key)
