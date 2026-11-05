# Kargo Gönderi Takip Sistemi

Kargo gönderilerinin oluşturulduğu, takip numarasıyla sorgulandığı ve durumlarının adım adım güncellendiği küçük ölçekli bir REST API uygulaması.

Bu proje, **YZM6443 Modern Yazılım Mühendisliği: Bulut ve DevOps** dersi dönem projesidir. Projenin asıl amacı, küçük bir uygulamanın yazılım yaşam döngüsünü Agile, DevOps ve Cloud yaklaşımlarıyla uçtan uca yönetmektir. Bu kapsamda Git, otomatik test, CI/CD, Docker, bulut dağıtımı ve izleme uygulanmaktadır.

| | |
|---|---|
| **Öğrenci** | Ece Melisa Şerik |
| **Ders** | YZM6443 – 2026-2027 Güz |
| **Sektör** | Lojistik |

## Temel Fonksiyonlar

| # | Fonksiyon | Endpoint |
|---|---|---|
| F1 | Gönderi oluşturma ve takip numarası üretimi | `POST /shipments` |
| F2 | Takip numarasıyla sorgulama ve hareket geçmişi | `GET /shipments/{takip_no}` |
| F3 | Durum güncelleme (kurallı geçişlerle) | `PATCH /shipments/{takip_no}/status` |
| F4 | Gönderi listeleme ve duruma göre filtreleme | `GET /shipments?status=...` |
| – | Sağlık kontrolü (izleme için) | `GET /health` |

## Fonksiyonel Gereksinimler

- **FR-1:** Sistem gönderici, alıcı, çıkış şehri ve varış şehri bilgileriyle yeni bir gönderi oluşturabilmelidir.
- **FR-2:** Her gönderiye UPU S10 standardına uygun, 13 karakterlik, kontrol haneli bir takip numarası atanmalıdır (örnek: `KG473124829TR`).
- **FR-3:** Yeni gönderinin ilk durumu otomatik olarak *Kabul edildi* olmalı ve hareket geçmişine kaydedilmelidir.
- **FR-4:** Takip numarasıyla sorgulandığında gönderinin güncel durumu ve tüm hareket geçmişi (zaman ve konum) dönmelidir.
- **FR-5:** Kontrol hanesi hatalı bir takip numarası veritabanına sorgu yapılmadan reddedilmelidir (`422`). Sistemde olmayan bir numara için `404` dönmelidir.
- **FR-6:** Gönderi durumu yalnızca izin verilen geçişlerle güncellenebilmelidir. Geçersiz bir geçiş `409` hatasıyla reddedilmelidir.
- **FR-7:** Her durum değişikliği, zaman ve konum bilgisiyle hareket geçmişine yeni bir kayıt olarak eklenmelidir. Önceki kayıtların üzerine yazılmamalıdır.
- **FR-8:** Gönderiler listelenebilmeli ve duruma göre filtrelenebilmelidir.
- **FR-9:** Sistem, uygulamanın ve veritabanının çalışıp çalışmadığını gösteren bir sağlık kontrolü endpoint'i sunmalıdır.

### Gönderi Durum Akışı

```
Kabul edildi → Transfer merkezinde → Dağıtıma çıktı → Teslim edildi
                                          ↓
                                   Teslim edilemedi → Dağıtıma çıktı (tekrar)
                                          ↓
                                       İade edildi
```

Ayrıntılı geçiş kuralları için: [docs/architecture.md](docs/architecture.md)

### Kapsam Dışı

Ders yönergesine uygun olarak aşağıdakiler kapsam dışıdır:

- Kullanıcı girişi ve yetkilendirme
- Ödeme ve ücret hesaplama
- Gelişmiş web arayüzü (API, FastAPI'nin otomatik Swagger arayüzü üzerinden kullanılır)
- Gerçek kargo firması entegrasyonu

## Kullanılan Teknolojiler

| Alan | Teknoloji |
|---|---|
| Uygulama | Python 3.12, FastAPI |
| Veritabanı | SQLite |
| Test | pytest |
| Kod kalitesi | Ruff |
| CI/CD | GitHub Actions |
| Konteyner | Docker |
| Bulut (PaaS) | Render |
| Proje yönetimi | GitHub Projects (Kanban) |

## Proje Yapısı

```
kargo-takip-devops/
├── src/                  # Uygulama kaynak kodları
├── tests/                # Otomatik testler
├── docs/                 # Mimari doküman
│   └── architecture.md
├── .github/workflows/    # GitHub Actions CI/CD
├── Dockerfile            # (5. hafta)
├── requirements.txt      # Python bağımlılıkları
├── .gitignore
└── README.md
```

## Kurulum ve Çalıştırma

> Bu bölüm uygulama geliştirildikçe (2. hafta) güncellenecektir.

```bash
git clone https://github.com/ecemserik/kargo-takip-devops.git
cd kargo-takip-devops
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## DevOps Yol Haritası

| Hafta | Çalışma | Durum |
|---|---|---|
| 1 | Gereksinimler, mimari, Git deposu, README, Kanban | 🔄 |
| 2 | Temel fonksiyonların ilk sürümü | ⏳ |
| 3 | Feature branch, Pull Request, merge | ⏳ |
| 4 | Otomatik testler (pytest), GitHub Actions CI | ⏳ |
| 5 | Dockerfile, Docker image, container | ⏳ |
| 6 | Render'a bulut dağıtımı | ⏳ |
| 7 | CD, health check, loglama, izleme, güvenlik taraması | ⏳ |
| 8 | Son testler, dokümantasyon, final sunumu | ⏳ |

## Bağlantılar

- **Kanban Panosu:** https://github.com/users/ecemserik/projects/1
- **Git Deposu:** https://github.com/ecemserik/kargo-takip-devops
- **Bulut Uygulaması:** _6. haftada eklenecek_
