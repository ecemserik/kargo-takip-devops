"""Veritabanı işlemleri (gönderi ekleme ve okuma)."""

import sqlite3
from datetime import datetime, timezone

from app.statuses import KABUL_EDILDI, STATUS_LABELS
from app.tracking import generate_tracking_no


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_shipment(conn: sqlite3.Connection, data: dict) -> str:
    """Yeni gönderi ve ilk hareket kaydını ("Kabul edildi") ekler. Takip numarasını döndürür."""
    now = _now()

    # Rastgele üretilen numara nadiren de olsa var olan bir numarayla çakışabilir; o yüzden kontrol et.
    tracking_no = generate_tracking_no()
    while conn.execute(
        "SELECT 1 FROM shipments WHERE tracking_no = ?", (tracking_no,)
    ).fetchone():
        tracking_no = generate_tracking_no()

    cur = conn.execute(
        """INSERT INTO shipments
           (tracking_no, sender_name, receiver_name, origin_city,
            destination_city, current_status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            tracking_no,
            data["sender_name"],
            data["receiver_name"],
            data["origin_city"],
            data["destination_city"],
            KABUL_EDILDI,
            now,
            now,
        ),
    )
    conn.execute(
        """INSERT INTO tracking_events (shipment_id, status, location, created_at)
           VALUES (?, ?, ?, ?)""",
        (cur.lastrowid, KABUL_EDILDI, f"{data['origin_city']} Şube", now),
    )
    conn.commit()
    return tracking_no


def get_shipment_detail(conn: sqlite3.Connection, tracking_no: str) -> dict | None:
    """Gönderiyi hareket geçmişiyle birlikte döndürür. Bulunamazsa None döner."""
    row = conn.execute(
        "SELECT * FROM shipments WHERE tracking_no = ?", (tracking_no,)
    ).fetchone()
    if row is None:
        return None

    events = conn.execute(
        """SELECT status, location, note, created_at FROM tracking_events
           WHERE shipment_id = ? ORDER BY created_at, id""",
        (row["id"],),
    ).fetchall()

    return {
        "tracking_no": row["tracking_no"],
        "sender_name": row["sender_name"],
        "receiver_name": row["receiver_name"],
        "origin_city": row["origin_city"],
        "destination_city": row["destination_city"],
        "current_status": row["current_status"],
        "current_status_label": STATUS_LABELS[row["current_status"]],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "events": [
            {
                "status": e["status"],
                "status_label": STATUS_LABELS[e["status"]],
                "location": e["location"],
                "note": e["note"],
                "created_at": e["created_at"],
            }
            for e in events
        ],
    }


def update_status(
    conn: sqlite3.Connection,
    tracking_no: str,
    new_status: str,
    location: str,
    note: str | None,
) -> None:
    """Gönderinin durumunu günceller ve hareket geçmişine yeni kayıt ekler."""
    now = _now()
    row = conn.execute(
        "SELECT id FROM shipments WHERE tracking_no = ?", (tracking_no,)
    ).fetchone()
    conn.execute(
        """INSERT INTO tracking_events (shipment_id, status, location, note, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (row["id"], new_status, location, note, now),
    )
    conn.execute(
        "UPDATE shipments SET current_status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, row["id"]),
    )
    conn.commit()


def list_shipments(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    """Gönderileri son güncellenene göre sıralı listeler; istenirse duruma göre filtreler."""
    query = "SELECT * FROM shipments"
    params: tuple = ()
    if status is not None:
        query += " WHERE current_status = ?"
        params = (status,)
    query += " ORDER BY updated_at DESC"

    rows = conn.execute(query, params).fetchall()
    return [
        {
            "tracking_no": r["tracking_no"],
            "sender_name": r["sender_name"],
            "receiver_name": r["receiver_name"],
            "origin_city": r["origin_city"],
            "destination_city": r["destination_city"],
            "current_status": r["current_status"],
            "current_status_label": STATUS_LABELS[r["current_status"]],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]
