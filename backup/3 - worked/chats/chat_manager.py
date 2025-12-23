from kivy.clock import Clock
from .database import ChatsDatabase


class ChatManager:
    def __init__(self):
        self.chats_db = ChatsDatabase()
        self.current_user = None
        self.current_chat_id = None

    def set_current_user(self, user):
        self.current_user = user

    def get_user_chats(self):
        if not self.current_user:
            return []
        return self.chats_db.get_user_chats(self.current_user['uid'])

    def create_chat(self, other_uid):
        if not self.current_user:
            return None
        return self.chats_db.create_or_get_chat(self.current_user['uid'], other_uid)

    def get_chat_messages(self, chat_id):
        return self.chats_db.get_chat_messages(chat_id)

    def send_message(self, chat_id, text):
        if not self.current_user:
            return False

        self.chats_db.add_message(chat_id, self.current_user['uid'], text)
        return True

    def search_users(self, search_term, users_db):
        if not self.current_user:
            return []
        return self.chats_db.search_users(search_term, self.current_user['uid'], users_db)
