from django import template
import re,memcache

register = template.Library()
def datinha(value):
    """Removes all values of arg from the given string"""
    return value.strftime("%Y-%m-%d %H:%M:%S")
register.filter('datinha', datinha)

def item(a,i):
    return a[i]
register.filter('item', item)

def rowcolor(a, uid):
    m=re.search("^\d+",a[2])
    if m is None:
        return ""
    d=m.group()
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    old_day = mc.get('last_day_%s'%(uid,))
    print("oi %s"%(old_day))
    if old_day is not None:
        day,color=re.split("_",old_day)
        if day!=d:
            if color=="#FFFFFF":
                color="#D3D3D3"
            else:
                color="#FFFFFF"
    else:
        color="#FFFFFF"
    mc.set('last_day_%s'%(uid,),"%s_%s"%(d,color))
    return color
register.filter('rowcolor', rowcolor)