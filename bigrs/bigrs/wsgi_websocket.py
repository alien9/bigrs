import os
import gevent.socket
import redis.connection
redis.connection.socket = gevent.socket
os.environ.update("DJANGO_SETTINGS_MODULE", "bigrs.settings")
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()