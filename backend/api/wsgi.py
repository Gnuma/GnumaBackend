import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

path = "/root/quipu/backend"

if path not in sys.path:
    sys.path.append(path)

application = get_wsgi_application()
