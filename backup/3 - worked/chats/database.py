import sqlite3
from datetime import datetime
import threading


class ChatsDatabase:
    def __init__(self, db_name='data_chats.db'):
        self.local = threading.local()
        self.db_name = db_name
        self._get_connection()
        self.create_tables()

    def _get_connection(self):
        """Получает соединение для текущего потока"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_name, timeout=30.0, check_same_thread=False)
            self.local.cursor = self.local.conn.cursor()
        return self.local.conn, self.local.cursor

    def create_tables(self):
        """Создает таблицы"""
        conn, cursor = self._get_connection()

        # Таблица чатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid1 TEXT NOT NULL,
                uid2 TEXT NOT NULL,
                last_message_time TEXT,
                UNIQUE(uid1, uid2)
            )
        ''')

        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender_uid TEXT NOT NULL,
                message_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
            )
        ''')

        conn.commit()

    def create_or_get_chat(self, uid1, uid2):
        """Создает или получает чат"""
        conn, cursor = self._get_connection()

        user1, user2 = sorted([uid1, uid2])

        cursor.execute('SELECT chat_id FROM chats WHERE uid1 = ? AND uid2 = ?', (user1, user2))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            cursor.execute('INSERT INTO chats (uid1, uid2, last_message_time) VALUES (?, ?, ?)',
                           (user1, user2, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def add_message(self, chat_id, sender_uid, message_text):
        """Добавляет сообщение"""
        conn, cursor = self._get_connection()

        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO messages (chat_id, sender_uid, message_text, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, sender_uid, message_text, timestamp))

        cursor.execute('UPDATE chats SET last_message_time = ? WHERE chat_id = ?',
                       (timestamp, chat_id))
        conn.commit()
        return cursor.lastrowid

    def get_user_chats(self, user_uid):
        """Получает чаты пользователя"""
        conn, cursor = self._get_connection()

        cursor.execute('''
            SELECT c.chat_id, c.uid1, c.uid2, c.last_message_time,
                   m.message_text, m.timestamp, m.sender_uid
            FROM chats c
            LEFT JOIN messages m ON m.message_id = (
                SELECT message_id FROM messages 
                WHERE chat_id = c.chat_id 
                ORDER BY timestamp DESC LIMIT 1
            )
            WHERE c.uid1 = ? OR c.uid2 = ?
            ORDER BY c.last_message_time DESC
        ''', (user_uid, user_uid))

        chats = []
        for chat in cursor.fetchall():
            chat_id, uid1, uid2, last_time, last_msg, msg_time, sender_uid = chat
            other_uid = uid2 if uid1 == user_uid else uid1

            chats.append({
                'chat_id': chat_id,
                'other_uid': other_uid,
                'last_message': last_msg or '',
                'last_message_time': last_time,
                'last_message_sender': sender_uid
            })

        return chats

    def get_chat_messages(self, chat_id, limit=50):
        """Получает сообщения чата"""
        conn, cursor = self._get_connection()

        cursor.execute('''
            SELECT message_id, sender_uid, message_text, timestamp
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (chat_id, limit))

        messages = []
        for msg in cursor.fetchall():
            msg_id, sender_uid, text, timestamp = msg
            messages.append({
                'id': msg_id,
                'sender_uid': sender_uid,
                'text': text,
                'timestamp': timestamp,
                'time_display': self._format_time(timestamp)
            })

        return messages

    def _format_time(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%H:%M')
        except:
            return timestamp

    def close(self):
        """Закрывает соединение"""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()