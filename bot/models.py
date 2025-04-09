# bot/models.py
import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            manga_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            manga_name TEXT,
            chapter INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_favorite(user_id, manga_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO favorites (user_id, manga_name) VALUES (?, ?)', (user_id, manga_name))
    conn.commit()
    conn.close()

def add_progress(user_id, manga_name, chapter):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO progress (user_id, manga_name, chapter) VALUES (?, ?, ?)', (user_id, manga_name, chapter))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT manga_name FROM favorites WHERE user_id = ?', (user_id,))
    favorites = cursor.fetchall()
    conn.close()
    return [row[0] for row in favorites]
