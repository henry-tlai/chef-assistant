import sqlite3

DB_PATH = "chef.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                recipe TEXT NOT NULL
            )
        """),
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)


def save_favorite(title, recipe):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO favorites (title, recipe) VALUES (?, ?)",
            (title, recipe),
        )

def list_favorites():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id, title FROM favorites").fetchall()
    return rows

def get_favorite(favorite_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT title, recipe FROM favorites WHERE id = ?",   
            (favorite_id,),                                              
        ).fetchone()
    return row

def delete_favorite(favorite_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "DELETE FROM favorites WHERE id = ?",
            (favorite_id,),
        )
    return cur.rowcount > 0

def save_messages(session_id, json_messages):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT INTO messages (session_id, content) VALUES (?, ?)",
            [(session_id, m) for m in json_messages],
        )


def load_messages(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT content FROM messages WHERE session_id = ? ORDER BY id",   # blank 2
            (session_id,),
        ).fetchall()
    return [row[0] for row in rows]

if __name__ == "__main__":
    init_db()
    print(list_favorites())
    print(get_favorite(1))
    print(get_favorite(999))
    save_messages("test", ['{"a": 1}', '{"b": 2}'])
    print(load_messages("test"))