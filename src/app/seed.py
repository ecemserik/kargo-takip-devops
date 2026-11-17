"""Örnek veri yükleme.

Render'ın ücretsiz planında dosya sistemi kalıcı değildir; her deploy veya yeniden
başlatmada veritabanı silinir. Bu yüzden uygulama her açılışta, veritabanı boşsa,
örnek gönderilerle kendini doldurur.
"""

from datetime import datetime, timedelta, timezone

from app.database import get_connection
from app.statuses import (
    DAGITIMA_CIKTI,
    KABUL_EDILDI,
    TESLIM_EDILDI,
    TRANSFER_MERKEZINDE,
)

# Takip numaraları S10 standardına uygundur (kontrol haneleri doğru hesaplanmıştır).
SAMPLE_SHIPMENTS = [
    {
        "tracking_no": "KG100000175TR",
        "sender_name": "Ayşe Yılmaz",
        "receiver_name": "Mehmet Demir",
        "origin_city": "İstanbul",
        "destination_city": "Ankara",
        "events": [
            (KABUL_EDILDI, "İstanbul Kadıköy Şube"),
            (TRANSFER_MERKEZINDE, "İstanbul Anadolu Transfer Merkezi"),
            (TRANSFER_MERKEZINDE, "Ankara Transfer Merkezi"),
            (DAGITIMA_CIKTI, "Ankara Çankaya Şube"),
            (TESLIM_EDILDI, "Ankara Çankaya"),
        ],
    },
    {
        "tracking_no": "KG200004524TR",
        "sender_name": "Can Kaya",
        "receiver_name": "Elif Şahin",
        "origin_city": "İzmir",
        "destination_city": "Bursa",
        "events": [
            (KABUL_EDILDI, "İzmir Bornova Şube"),
            (TRANSFER_MERKEZINDE, "İzmir Transfer Merkezi"),
        ],
    },
    {
        "tracking_no": "KG300008965TR",
        "sender_name": "Zeynep Arslan",
        "receiver_name": "Burak Çelik",
        "origin_city": "Antalya",
        "destination_city": "İstanbul",
        "events": [
            (KABUL_EDILDI, "Antalya Muratpaşa Şube"),
        ],
    },
]


def seed_if_empty() -> None:
    """Veritabanında hiç gönderi yoksa örnek gönderileri ekler."""
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
        if count > 0:
            return

        start = datetime.now(timezone.utc) - timedelta(days=3)
        for shipment in SAMPLE_SHIPMENTS:
            events = shipment["events"]
            created = start.isoformat()
            last_status = events[-1][0]
            cur = conn.execute(
                """INSERT INTO shipments
                   (tracking_no, sender_name, receiver_name, origin_city,
                    destination_city, current_status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    shipment["tracking_no"],
                    shipment["sender_name"],
                    shipment["receiver_name"],
                    shipment["origin_city"],
                    shipment["destination_city"],
                    last_status,
                    created,
                    created,
                ),
            )
            shipment_id = cur.lastrowid
            for i, (status, location) in enumerate(events):
                event_time = (start + timedelta(hours=8 * i)).isoformat()
                conn.execute(
                    """INSERT INTO tracking_events (shipment_id, status, location, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (shipment_id, status, location, event_time),
                )
                conn.execute(
                    "UPDATE shipments SET updated_at = ? WHERE id = ?",
                    (event_time, shipment_id),
                )
        conn.commit()
    finally:
        conn.close()
