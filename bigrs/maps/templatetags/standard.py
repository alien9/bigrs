from django import template

register = template.Library()
def datinha(value):
    """Removes all values of arg from the given string"""
    return value.strftime("%Y-%m-%d %H:%M:%S")
register.filter('datinha', datinha)

def item(a,i):
    return a[i]
register.filter('item', item)