"""UPU S10 standardına uygun takip numarası üretimi ve doğrulaması.

Format: AA 12345678 9 BB  (toplam 13 karakter)
  AA       -> hizmet kodu (bu projede "KG")
  12345678 -> 8 haneli seri numarası
  9        -> kontrol hanesi
  BB       -> ülke kodu ("TR")
"""

import random
import re

SERVICE_CODE = "KG"
COUNTRY_CODE = "TR"
WEIGHTS = [8, 6, 4, 2, 3, 5, 9, 7]

_S10_PATTERN = re.compile(r"^[A-Z]{2}\d{9}[A-Z]{2}$")


def compute_check_digit(serial: str) -> int:
    """8 haneli seri numarasının kontrol hanesini hesaplar."""
    if len(serial) != 8 or not serial.isdigit():
        raise ValueError("Seri numarası 8 rakamdan oluşmalıdır")
    total = sum(int(digit) * weight for digit, weight in zip(serial, WEIGHTS))
    check = 11 - (total % 11)
    if check == 10:
        return 0
    if check == 11:
        return 5
    return check


def build_tracking_no(serial: str) -> str:
    """Seri numarasından tam takip numarasını oluşturur. Örn: 47312482 -> KG473124829TR"""
    return f"{SERVICE_CODE}{serial}{compute_check_digit(serial)}{COUNTRY_CODE}"


def generate_tracking_no() -> str:
    """Rastgele seri numarasıyla yeni bir takip numarası üretir."""
    serial = f"{random.randint(0, 99_999_999):08d}"
    return build_tracking_no(serial)


def is_valid_tracking_no(tracking_no: str) -> bool:
    """Takip numarasının formatını ve kontrol hanesini doğrular."""
    if not _S10_PATTERN.match(tracking_no):
        return False
    serial = tracking_no[2:10]
    check_digit = int(tracking_no[10])
    return compute_check_digit(serial) == check_digit
