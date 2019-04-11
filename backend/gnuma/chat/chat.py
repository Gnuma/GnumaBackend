from channels.generic.websocket import WebsocketConsumer

class BasicChatConsumer(WebsocketConsumer):
    
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        response = text_data[::-1]
        self.send(text_data = response)