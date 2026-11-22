"""Gönderi uç noktaları (endpoints)."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import repository
from app.database import get_db
from app.schemas import (
    ShipmentCreate,
    ShipmentDetail,
    ShipmentSummary,
    StatusCode,
    StatusUpdate,
)
from app.statuses import ALLOWED_TRANSITIONS, STATUS_LABELS, can_transition
from app.tracking import is_valid_tracking_no

router = APIRouter(prefix="/shipments", tags=["Gönderiler"])

# Her istekte veritabanı bağlantısını FastAPI otomatik verir
DB = Annotated[sqlite3.Connection, Depends(get_db)]


@router.post("", response_model=ShipmentDetail, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, conn: DB):
    """F1: Yeni gönderi oluşturur ve S10 standardında takip numarası üretir."""
    tracking_no = repository.create_shipment(conn, payload.model_dump())
    return repository.get_shipment_detail(conn, tracking_no)


@router.get("", response_model=list[ShipmentSummary])
def list_shipments(conn: DB, status: StatusCode | None = None):
    """F4: Gönderileri listeler. status parametresiyle duruma göre filtrelenebilir."""
    return repository.list_shipments(conn, status)


@router.get(
    "/{tracking_no}",
    response_model=ShipmentDetail,
    responses={
        404: {"description": "Bu takip numarasıyla gönderi bulunamadı"},
        422: {
            "description": "Takip numarası geçersiz (format veya kontrol hanesi hatalı)"
        },
    },
)
def get_shipment(tracking_no: str, conn: DB):
    """F2: Takip numarasıyla gönderiyi ve hareket geçmişini getirir."""
    tracking_no = _validate_tracking_no(tracking_no)
    return _get_or_404(conn, tracking_no)


@router.patch(
    "/{tracking_no}/status",
    response_model=ShipmentDetail,
    responses={
        404: {"description": "Bu takip numarasıyla gönderi bulunamadı"},
        409: {"description": "Bu durum geçişine izin verilmiyor"},
        422: {"description": "Takip numarası veya istek gövdesi geçersiz"},
    },
)
def update_shipment_status(tracking_no: str, payload: StatusUpdate, conn: DB):
    """F3: Gönderi durumunu günceller. Yalnızca izin verilen geçişler kabul edilir."""
    tracking_no = _validate_tracking_no(tracking_no)
    shipment = _get_or_404(conn, tracking_no)

    current = shipment["current_status"]
    if not can_transition(current, payload.status):
        allowed = [STATUS_LABELS[s] for s in sorted(ALLOWED_TRANSITIONS[current])]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "mesaj": (
                    f"'{STATUS_LABELS[current]}' durumundan "
                    f"'{STATUS_LABELS[payload.status]}' durumuna geçilemez"
                ),
                "izin_verilen_durumlar": allowed,
            },
        )

    repository.update_status(
        conn, tracking_no, payload.status, payload.location, payload.note
    )
    return repository.get_shipment_detail(conn, tracking_no)


# ---------- Yardımcı fonksiyonlar ----------


def _validate_tracking_no(tracking_no: str) -> str:
    """Takip numarasını büyük harfe çevirir; format veya kontrol hanesi hatalıysa 422 verir."""
    tracking_no = tracking_no.strip().upper()
    if not is_valid_tracking_no(tracking_no):
        raise HTTPException(
            status_code=422,
            detail="Geçersiz takip numarası: format veya kontrol hanesi hatalı",
        )
    return tracking_no


def _get_or_404(conn, tracking_no: str) -> dict:
    """Gönderiyi getirir; yoksa 404 verir."""
    shipment = repository.get_shipment_detail(conn, tracking_no)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu takip numarasıyla gönderi bulunamadı",
        )
    return shipment
