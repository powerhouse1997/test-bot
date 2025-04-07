from tinydb import TinyDB, Query
from bot.database import todos

users = set()
todos = {}

def save_user(chat_id):
    users.add(chat_id)

def get_all_users():
    return list(users)

db = TinyDB('db.json')
reminders_table = db.table('reminders')
todos_table = db.table('todos')

def add_reminder(chat_id, time, text):
    reminders_table.insert({'chat_id': chat_id, 'time': time, 'text': text})

def get_reminders(chat_id):
    return reminders_table.search(Query().chat_id == chat_id)

def add_todo(chat_id, task):
    todos_table.insert({'chat_id': chat_id, 'task': task, 'done': False})

def get_todos(chat_id):
    return todos_table.search((Query().chat_id == chat_id) & (Query().done == False))

def complete_todo(chat_id, index):
    todos = get_todos(chat_id)
    if 0 <= index < len(todos):
        todos_table.update({'done': True}, doc_ids=[todos[index].doc_id])
