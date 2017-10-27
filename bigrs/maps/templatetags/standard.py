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

def rowcolor(a, uid):
    m=re.search("^\d+",a[2])
    if m is None:
        return ""
    d=m.group()
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    old_day = mc.get('last_day_%s'%(uid,))
    #print("oi %s"%(old_day))
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

def locator(a, uid):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    old_cont = mc.get('last_contagem_%s'%(uid,))
    if old_cont=='None':
        old_cont=0
    if old_cont is None:
        old_cont=0
    if old_cont != a[13]:
        mc.set('last_contagem_%s' % (uid,), a[13])
        return "<td rowspan=\"5\"><img src=\"/sentidos?contagem_id="+str(a[13])+"\" style=\"width:200px;height:200px;\"></td>"
    else:
        return ""

register.filter('locator', locator)
register.filter('rowcolor', rowcolor)