from gnuma.core.authToken import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import gnuma.routing

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            gnuma.routing.websocket_urlpatterns
        )
    ),
})