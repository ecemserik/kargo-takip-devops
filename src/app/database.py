"""SQLite veritabanı bağlantısı ve tablo oluşturma."""

import os
import sqlite3

# Veritabanı dosyasının yolu ortam değişkeninden okunur (bulutta değiştirilebilsin diye).
DB_PATH = os.getenv("DB_PATH", "kargo.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS shipments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_no      TEXT    NOT NULL UNIQUE,
    sender_name      TEXT    NOT NULL,
    receiver_name    TEXT    NOT NULL,
    origin_city      TEXT    NOT NULL,
    destination_city TEXT    NOT NULL,
    current_status   TEXT    NOT NULL,
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS tracking_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id  INTEGER NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    status       TEXT    NOT NULL,
    location     TEXT    NOT NULL,
    note         TEXT,
    created_at   TEXT    NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    """Yeni bir veritabanı bağlantısı açar. Satırlara sütun adıyla erişilebilir (row['tracking_no'])."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """FastAPI bağımlılığı: her istek için bağlantı açar, istek bitince kapatır."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Tablolar yoksa oluşturur."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
