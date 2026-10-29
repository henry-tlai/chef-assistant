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

if __name__ == "__main__":
    init_db()
    print(list_favorites())
    print(get_favorite(1))
    print(get_favorite(999))