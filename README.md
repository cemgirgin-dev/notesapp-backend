# Notes App Backend

> 🇹🇷 Aşağıda Türkçe ve İngilizce kurulum bilgilerinin her ikisi de yer alır.  
> 🇬🇧 Instructions in both Turkish and English are provided below.

---

## Türkçe

SwiftUI istemcisi için geliştirilen FastAPI tabanlı not alma servisidir. Kimlik doğrulama, not CRUD işlemleri ve PDF çıktısı üretimi içerir.

### Özellikler
- JWT tabanlı kimlik doğrulama (kayıt ol, giriş yap, `/auth/me`).
- Kullanıcıya özel not oluşturma, görüntüleme, güncelleme, silme.
- Her notu PDF olarak indirme (`/notes/{id}/pdf`).

### Gereksinimler
- Python 3.9+
- `virtualenv` veya `venv` (önerilen)
- SQLite (varsayılan) ya da uyumlu başka bir SQL veritabanı

### Kurulum
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Ortam Değişkenleri
Aşağıdaki değişkenler `.env` dosyası veya kabuk ortamında tanımlanmalıdır:

| Değişken | Açıklama | Varsayılan |
| --- | --- | --- |
| `SECRET_KEY` | JWT üretimi için gizli anahtar. Güvenli, tahmin edilemez bir değer kullanın. `openssl rand -hex 32` ile oluşturabilirsiniz. | `change-me-to-a-secure-value` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token geçerliliği (dakika). | `60` |
| `DATABASE_URL` | SQLAlchemy bağlantı adresi. SQLite için `sqlite:///./notes.db`. | `sqlite:///./notes.db` |

Örnek `.env`:
```dotenv
SECRET_KEY=super-guvenli-bir-anahtar
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./notes.db
```

### Çalıştırma
```bash
./scripts/run.sh
```

Script, `.env` dosyası varsa yükler ve Uvicorn’u `http://127.0.0.1:8000` adresinde başlatır. Geliştirme sırasında otomatik yeniden yükleme için `--reload` parametresi script içerisinde aktiftir.

### API Hızlı Bakış
- `POST /auth/signup` – Yeni kullanıcı oluşturur.
- `POST /auth/login` – JWT token döner.
- `GET /auth/me` – Kullanıcı profili.
- `GET /notes/` – Kullanıcının notları.
- `POST /notes/` – Yeni not.
- `GET /notes/{note_id}` – Not detayı.
- `PUT /notes/{note_id}` – Notu günceller.
- `DELETE /notes/{note_id}` – Notu siler.
- `GET /notes/{note_id}/pdf` – Notu PDF olarak indirir.

Tüm korumalı uç noktalar `Authorization: Bearer <token>` başlığı gerektirir.

### SwiftUI İstemcisi
SwiftUI tarafındaki model ve servis örnekleri için `docs/swift-guide.md` dosyasına bakın. Bu rehberde `User`, `Note`, `AuthResponse` modelleri ve temel API çağrıları yer almaktadır.

### Test / Doğrulama
```bash
python3 -m compileall app
```

### Dağıtım Notları
- Üretimde `SECRET_KEY` çevresel değişkeni zorunlu.
- SQLite tek kullanıcı için yeterlidir; çoklu örnek için Postgres gibi harici veritabanı önerilir.
- CORS tüm kaynaklara açık; üretimde sadece gerekli origin’leri listeleyin.

---

## English

FastAPI backend that powers a SwiftUI notes client. Provides authentication, note CRUD endpoints, and PDF export per note.

### Features
- JWT-based authentication (sign up, sign in, `/auth/me`).
- Per-user note creation, retrieval, update, and delete.
- Export individual notes as PDF (`/notes/{id}/pdf`).

### Requirements
- Python 3.9+
- `virtualenv` or `venv` (recommended)
- SQLite (default) or any SQL database supported by SQLAlchemy

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables
Define the following either in a `.env` file or directly in your shell:

| Variable | Description | Default |
| --- | --- | --- |
| `SECRET_KEY` | Secret used to sign JWTs. Replace with a secure random value (`openssl rand -hex 32`). | `change-me-to-a-secure-value` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes. | `60` |
| `DATABASE_URL` | SQLAlchemy connection string. Use `sqlite:///./notes.db` for local SQLite. | `sqlite:///./notes.db` |

Sample `.env`:
```dotenv
SECRET_KEY=replace-me-with-a-secure-value
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./notes.db
```

### Run
```bash
./scripts/run.sh
```

The script loads `.env` if present and starts Uvicorn at `http://127.0.0.1:8000` with reload enabled for development.

### API Quick Reference
- `POST /auth/signup` – Register a new user.
- `POST /auth/login` – Issue JWT access token.
- `GET /auth/me` – Return current user profile.
- `GET /notes/` – List notes for the authenticated user.
- `POST /notes/` – Create a new note.
- `GET /notes/{note_id}` – Fetch note details.
- `PUT /notes/{note_id}` – Update a note.
- `DELETE /notes/{note_id}` – Delete a note.
- `GET /notes/{note_id}/pdf` – Download note as PDF.

All protected endpoints require an `Authorization: Bearer <token>` header.

### SwiftUI Client
Implementation guidance, data models, and service layer examples are available in `docs/swift-guide.md`.

### Verify
```bash
python3 -m compileall app
```

### Deployment Notes
- `SECRET_KEY` must be set through environment variables in production.
- SQLite is suitable for local development; use Postgres or similar for multi-user deployments.
- CORS is wide open for development; restrict `allow_origins` before shipping.
