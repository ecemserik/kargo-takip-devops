"""Gönderi durumları."""

KABUL_EDILDI = "KABUL_EDILDI"
TRANSFER_MERKEZINDE = "TRANSFER_MERKEZINDE"
DAGITIMA_CIKTI = "DAGITIMA_CIKTI"
TESLIM_EDILDI = "TESLIM_EDILDI"
TESLIM_EDILEMEDI = "TESLIM_EDILEMEDI"
IADE_EDILDI = "IADE_EDILDI"

# Ekranda gösterilecek Türkçe karşılıklar
STATUS_LABELS = {
    KABUL_EDILDI: "Kabul edildi",
    TRANSFER_MERKEZINDE: "Transfer merkezinde",
    DAGITIMA_CIKTI: "Dağıtıma çıktı",
    TESLIM_EDILDI: "Teslim edildi",
    TESLIM_EDILEMEDI: "Teslim edilemedi",
    IADE_EDILDI: "İade edildi",
}

# İzin verilen durum geçişleri (docs/architecture.md - Bölüm 5)
ALLOWED_TRANSITIONS = {
    KABUL_EDILDI: {TRANSFER_MERKEZINDE},
    TRANSFER_MERKEZINDE: {TRANSFER_MERKEZINDE, DAGITIMA_CIKTI},
    DAGITIMA_CIKTI: {TESLIM_EDILDI, TESLIM_EDILEMEDI},
    TESLIM_EDILEMEDI: {DAGITIMA_CIKTI, IADE_EDILDI},
    TESLIM_EDILDI: set(),  # son durum
    IADE_EDILDI: set(),  # son durum
}


def can_transition(current: str, new: str) -> bool:
    """Mevcut durumdan yeni duruma geçişe izin var mı?"""
    return new in ALLOWED_TRANSITIONS.get(current, set())
