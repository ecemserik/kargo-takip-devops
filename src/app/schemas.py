"""API'nin aldığı ve döndürdüğü veri şekilleri (Pydantic modelleri)."""

from typing import Literal

from pydantic import BaseModel, Field

# API'de kabul edilen durum kodları (Swagger'da açılır liste olarak görünür)
StatusCode = Literal[
    "KABUL_EDILDI",
    "TRANSFER_MERKEZINDE",
    "DAGITIMA_CIKTI",
    "TESLIM_EDILDI",
    "TESLIM_EDILEMEDI",
    "IADE_EDILDI",
]


class ShipmentCreate(BaseModel):
    """Yeni gönderi oluştururken gönderilen bilgiler."""

    sender_name: str = Field(min_length=2, max_length=100, examples=["Ayşe Yılmaz"])
    receiver_name: str = Field(min_length=2, max_length=100, examples=["Mehmet Demir"])
    origin_city: str = Field(min_length=2, max_length=50, examples=["İstanbul"])
    destination_city: str = Field(min_length=2, max_length=50, examples=["Ankara"])


class TrackingEvent(BaseModel):
    """Gönderinin hareket geçmişindeki tek bir kayıt."""

    status: str
    status_label: str
    location: str
    note: str | None = None
    created_at: str


class ShipmentDetail(BaseModel):
    """Gönderi bilgileri ve hareket geçmişi."""

    tracking_no: str
    sender_name: str
    receiver_name: str
    origin_city: str
    destination_city: str
    current_status: str
    current_status_label: str
    created_at: str
    updated_at: str
    events: list[TrackingEvent]


class StatusUpdate(BaseModel):
    """Gönderi durumunu güncellerken gönderilen bilgiler."""

    status: StatusCode = Field(examples=["TRANSFER_MERKEZINDE"])
    location: str = Field(
        min_length=2, max_length=100, examples=["Ankara Transfer Merkezi"]
    )
    note: str | None = Field(default=None, max_length=200)
