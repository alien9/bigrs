from django import template
import re,memcache

register = template.Library()
def datinha(value):
    """Removes all values of arg from the given string"""
    return value.strftime("%Y-%m-%d %H:%M:%S")
register.filter('datinha', datinha)

def item(a,i):
    if a[i] is None:
        return 0
    return a[i]
register.filter('item', item)

def rowcolor(a):
    return a[14]

def locator(a):
    if a[15]!="":
        return "<td rowspan=\"15\" style=\"vertical-align:top;border:none\"><img src=\"/sentidos?contagem_id="+str(a[13])+"\" style=\"width:200px;height:200px;\"></td>"
    else:
        return ""

register.filter('locator', locator)
register.filter('rowcolor', rowcolor)