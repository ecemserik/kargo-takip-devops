"""Gönderi uç noktaları (endpoints)."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import repository
from app.database import get_db
from app.schemas import ShipmentCreate, ShipmentDetail
from app.tracking import is_valid_tracking_no

router = APIRouter(prefix="/shipments", tags=["Gönderiler"])

# Her istekte veritabanı bağlantısını FastAPI otomatik verir
DB = Annotated[sqlite3.Connection, Depends(get_db)]


@router.post("", response_model=ShipmentDetail, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, conn: DB):
    """F1: Yeni gönderi oluşturur ve S10 standardında takip numarası üretir."""
    tracking_no = repository.create_shipment(conn, payload.model_dump())
    return repository.get_shipment_detail(conn, tracking_no)


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
    tracking_no = tracking_no.strip().upper()

    # Kontrol hanesi hatalı numarayı veritabanına hiç sormadan reddet
    if not is_valid_tracking_no(tracking_no):
        raise HTTPException(
            status_code=422,
            detail="Geçersiz takip numarası: format veya kontrol hanesi hatalı",
        )

    shipment = repository.get_shipment_detail(conn, tracking_no)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu takip numarasıyla gönderi bulunamadı",
        )
    return shipment
