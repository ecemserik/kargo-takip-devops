"""Gönderi uç noktaları (endpoints)."""

import sqlite3

from fastapi import APIRouter, Depends, status

from app import repository
from app.database import get_db
from app.schemas import ShipmentCreate, ShipmentDetail

router = APIRouter(prefix="/shipments", tags=["Gönderiler"])


@router.post("", response_model=ShipmentDetail, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, conn: sqlite3.Connection = Depends(get_db)):
    """F1: Yeni gönderi oluşturur ve S10 standardında takip numarası üretir."""
    tracking_no = repository.create_shipment(conn, payload.model_dump())
    return repository.get_shipment_detail(conn, tracking_no)
