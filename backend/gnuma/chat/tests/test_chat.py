import pytest
import json
from asgiref.sync import sync_to_async
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator, HttpCommunicator
from api.routing import application
from channels.db import database_sync_to_async
from gnuma.chat.chat import Chat
from gnuma.chat.tests.factories import UserFactory, TokenFactory, ChatFactory, ItemFactory, GnumaUserFactory



@database_sync_to_async
def get_user(username):
    user = UserFactory(username = username)
    gnumaUser = GnumaUserFactory(user = user)
    return user
    
@database_sync_to_async
def get_token(user):
    token = TokenFactory(user = user)
    return token.key

@database_sync_to_async
def get_chat(buyer, item):
    chat = ChatFactory(buyer = GnumaUserFactory(user = buyer), item = item)
    return chat

@database_sync_to_async
def get_item(seller):
    item = ItemFactory(seller = GnumaUserFactory(user = seller))
    return item


@pytest.mark.asyncio
@pytest.mark.django_db(transaction = True)
async def test_connection():
    user = await get_user("Gnuma")
    token = await get_token(user)
    communicator = WebsocketCommunicator(application, r'ws/chat/?token={}'.format(token))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.disconnect()

@sync_to_async
def callAPI(path, body, token = None):
    c = APIClient()
    if token:
        c.credentials(HTTP_AUTHORIZATION = 'Token ' + token)
    response = c.post(path, json.dumps(body), content_type='application/json')
    return response

@pytest.mark.asyncio
@pytest.mark.django_db(transaction = True)
async def test_newMessage():
    #
    # Create the context to make this test work
    #
    seller = await get_user("Test6")
    buyer = await get_user("Gnuma")
    item = await get_item(seller)
    chat = await get_chat(buyer, item)
    token_seller = await get_token(seller)
    token_buyer = await get_token(buyer)
    #
    # Connecting the seller to the websocket
    #
    communicator = WebsocketCommunicator(application, r'ws/chat/?token={}'.format(token_seller))
    connected, _ = await communicator.connect()
    assert connected
    #
    # The buyer creates a new comment.
    #
    body = {}
    body['item'] = item.pk
    body['content'] = "Ciao, hai per caso pure la seconda edizione?"
    body['type'] = "comment"
    response = await callAPI('/gnuma/v1/comments/', body, token_buyer)
    #
    # The endpoint should return 201 CREATED.
    #
    assert response.status_code == 201 
    #
    # If everything went good, the server should send to seller the notification.
    #
    response = await communicator.receive_from()
    print(response)
    assert len(response) != 0
    #
    # Disconnecting the seller
    #
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction = True)
async def test_newAnswer():
    #
    # Create the context to make this test work
    #
    seller = await get_user("Test6")
    buyer = await get_user("Gnuma")
    item = await get_item(seller)
    chat = await get_chat(buyer, item)
    token_seller = await get_token(seller)
    token_buyer = await get_token(buyer)
    #
    # The buyer creates a new comment.
    #
    body = {}
    body['item'] = item.pk
    body['content'] = "Ciao, hai per caso pure la seconda edizione?"
    body['type'] = "comment"
    response = await callAPI('/gnuma/v1/comments/', body, token_buyer)
    #
    # The endpoint should return 201 CREATED.
    #
    assert response.status_code == 201 
    #
    # The buyer gets connected to the websocket.
    #
    communicator = WebsocketCommunicator(application, r'ws/chat/?token={}'.format(token_buyer))
    connected, _ = await communicator.connect()
    assert connected
    #
    # The seller answers to comment.
    # 
    body = {}
    body['item'] = 1 # it's always 1.
    body['content'] = "No, non ce l'ho!"
    body['type'] = "answer"
    response = await callAPI('/gnuma/v1/comments/', body, token_seller)
    #
    # The endpoint should return 201 CREATED.
    #
    assert response.status_code == 201
    #
    # If everything went good, the server should send to buyer the notification.
    #
    response = await communicator.receive_from()
    print(response)
    assert len(response) != 0
    #
    # Disconnecting the buyer
    #
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction = True)
async def test_newChat():
    #
    # Create the context to make this test work
    #
    seller = await get_user("seller")
    buyer = await get_user("buyer")
    item = await get_item(seller)
    token_seller = await get_token(seller)
    token_buyer = await get_token(buyer)
    #
    # The buyer gets connected to the websocket.
    #
    communicator = WebsocketCommunicator(application, r'ws/chat/?token={}'.format(token_seller))
    connected, _ = await communicator.connect()
    assert connected
    #
    # The buyer creates a new chat.
    #
    body = {}
    body['item'] = 1
    response = await callAPI('/gnuma/v1/chat/', body, token_buyer)
    #
    # The endpoint should return 201. 
    #
    assert response.status_code == 201
    #
    # If everything went good, the server should send to seller the notification.
    #
    response = await communicator.receive_from()
    print(response)
    assert len(response) != 0
    #
    # Disconnecting the seller
    #
    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction = True)
async def test_newMessage():
    #
    # Create the context to make this test work
    #
    seller = await get_user("seller")
    buyer = await get_user("buyer")
    item = await get_item(seller)
    token_seller = await get_token(seller)
    token_buyer = await get_token(buyer)