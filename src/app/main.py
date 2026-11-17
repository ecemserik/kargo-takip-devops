"""Kargo Gönderi Takip Sistemi - FastAPI uygulaması."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama açılırken: tabloları oluştur, boşsa örnek verileri yükle
    init_db()
    seed_if_empty()
    yield


app = FastAPI(
    title="Kargo Gönderi Takip Sistemi",
    description="Gönderi oluşturma, takip numarasıyla sorgulama ve durum takibi API'si.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Genel"])
def root():
    return {
        "uygulama": "Kargo Gönderi Takip Sistemi",
        "dokumantasyon": "/docs",
    }
