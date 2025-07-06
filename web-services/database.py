import sqlite3
from model import Service

DB_FILE = "services.db"

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Services (
            id          INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            url         TEXT    NOT NULL,
            description TEXT    NOT NULL,
            category    TEXT
        );
    """)
    conn.commit()
    conn.close()

def get_all_services() -> list[Service]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, url, description, category FROM Services ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return [Service(*row) for row in rows]

def get_service_by_id(service_id: int) -> Service | None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, url, description, category FROM Services WHERE id = ?;", (service_id,))
    row = cur.fetchone()
    conn.close()
    return Service(*row) if row else None

def add_service(svc: Service) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Services (name, url, description, category) VALUES (?, ?, ?, ?);",
        (svc.name, svc.url, svc.description, svc.category)
    )
    conn.commit()
    conn.close()

def update_service(svc: Service) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "UPDATE Services SET name = ?, url = ?, description = ?, category = ? WHERE id = ?;",
        (svc.name, svc.url, svc.description, svc.category, svc.id)
    )
    conn.commit()
    conn.close()

def delete_service(service_id: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM Services WHERE id = ?;", (service_id,))
    conn.commit()
    conn.close()
