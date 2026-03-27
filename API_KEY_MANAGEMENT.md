# API Key Management System

Bu sistem, kullanıcıların kendi API anahtarlarını oluşturup yönetebilmeleri için kapsamlı bir API anahtar yönetim sistemi sağlar.

## Özellikler

- ✅ Güvenli, rastgele API anahtarı üretimi (32+ karakter)
- ✅ API anahtarlarının veritabanında hash'lenerek saklanması (SHA-256)
- ✅ `sk_live_` ve `sk_test_` prefix formatı
- ✅ Anahtarların yalnızca oluşturma sırasında bir kez gösterilmesi
- ✅ API anahtarı doğrulama ve kimlik doğrulama
- ✅ Anahtar iptal etme/silme
- ✅ Son kullanım tarihlerinin takibi
- ✅ Opsiyonel son kullanma tarihi desteği
- ✅ Bearer token authentication middleware

## Kurulum

### 1. Veritabanı Başlatma

Öncelikle `api_keys` tablosunu veritabanınıza ekleyin:

```bash
python3 init_api_keys_db.py
```

Bu script aşağıdaki tabloyu oluşturur:

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    key_name TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    key_prefix TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_used_at TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    expires_at TEXT
)
```

## Kullanım

### API Anahtarı Oluşturma

```python
from api_key_manager import create_api_key

# Live API anahtarı oluştur
api_key, key_info = create_api_key(
    user_id="user123",
    key_name="Mobil Uygulama",
    key_type="live"
)

if api_key:
    print(f"Yeni API Anahtarınız: {api_key}")
    print(f"⚠️  Bu anahtarı güvenli bir yerde saklayın!")
    print(f"⚠️  Bir daha göremeyeceksiniz!")

# Test API anahtarı oluştur (30 gün sonra süresi dolar)
test_key, test_info = create_api_key(
    user_id="user123",
    key_name="Test Environment",
    key_type="test",
    expires_days=30
)
```

### API Anahtarını Doğrulama

```python
from api_key_manager import validate_api_key

key_data = validate_api_key(api_key)

if key_data:
    print(f"Geçerli anahtar!")
    print(f"Kullanıcı ID: {key_data['user_id']}")
    print(f"Anahtar Adı: {key_data['key_name']}")
else:
    print("Geçersiz veya süresi dolmuş anahtar!")
```

### API İsteğini Doğrulama (Middleware)

```python
from api_auth_middleware import authenticate_api_request

# HTTP Authorization header'ından
auth_header = "Bearer sk_live_xxxxxxxxxxxx"
auth_context = authenticate_api_request(auth_header)

if auth_context:
    user_id = auth_context['user_id']
    # İşleme devam et
else:
    # Yetkisiz erişim
    return {"error": "Unauthorized"}, 401
```

### Kullanıcının API Anahtarlarını Listeleme

```python
from api_key_manager import list_user_api_keys

keys = list_user_api_keys("user123")

for key in keys:
    print(f"{key['key_name']}: {key['key_prefix']}")
    print(f"  Durum: {'Aktif' if key['is_active'] else 'Pasif'}")
    print(f"  Oluşturulma: {key['created_at']}")
    if key['last_used_at']:
        print(f"  Son Kullanım: {key['last_used_at']}")
```

### API Anahtarını İptal Etme

```python
from api_key_manager import revoke_api_key

success = revoke_api_key(key_id=1, user_id="user123")

if success:
    print("Anahtar başarıyla iptal edildi!")
```

### API Anahtarını Silme

```python
from api_key_manager import delete_api_key

success = delete_api_key(key_id=1, user_id="user123")

if success:
    print("Anahtar kalıcı olarak silindi!")
```

## Web Framework Entegrasyonu

### Flask ile Kullanım

```python
from flask import Flask, request, jsonify
from api_auth_middleware import FlaskAPIAuthMiddleware

app = Flask(__name__)

# Middleware'i yapılandır
auth_middleware = FlaskAPIAuthMiddleware(
    excluded_paths=['/health', '/login']
)

@app.before_request
def check_auth():
    return auth_middleware.before_request(request)

@app.route('/api/data')
def get_data():
    # request.auth_context otomatik olarak doldurulur
    user_id = request.auth_context['user_id']
    return jsonify({'user_id': user_id, 'data': 'some data'})
```

### FastAPI ile Kullanım

```python
from fastapi import FastAPI, Depends, Header
from api_auth_middleware import get_api_auth

app = FastAPI()

@app.get("/api/data")
def get_data(
    auth: dict = Depends(get_api_auth),
    authorization: str = Header(None)
):
    user_id = auth['user_id']
    return {'user_id': user_id, 'data': 'some data'}
```

### Basit Fonksiyon Tabanlı Kontrol

```python
from api_auth_middleware import check_api_auth

def my_api_endpoint(authorization_header):
    is_authenticated, auth_context = check_api_auth(authorization_header)
    
    if not is_authenticated:
        return {"error": "Unauthorized"}, 401
    
    user_id = auth_context['user_id']
    # İşleme devam et...
```

## Örnek Kullanım

Tam bir örnek için `api_key_example.py` dosyasını çalıştırın:

```bash
python3 api_key_example.py
```

Bu script şunları gösterir:
- API anahtarı oluşturma
- Anahtarı doğrulama
- İstek kimlik doğrulama
- Anahtarları listeleme
- Anahtarı iptal etme

## Test Etme

Tüm testleri çalıştırmak için:

```bash
python3 test_api_keys.py
```

Test paketi şunları kapsar:
- Anahtar üretimi ve format kontrolü
- Hash fonksiyonları
- Anahtar oluşturma
- Anahtar doğrulama
- Anahtar iptal etme
- Kimlik doğrulama middleware
- Edge case'ler ve hata yönetimi

## Güvenlik Kontrol Listesi

- ✅ **Asla düz metin saklanmıyor**: API anahtarları veritabanında SHA-256 hash'i olarak saklanır
- ✅ **Bir kez gösterilme**: Anahtarlar yalnızca oluşturma sırasında düz metin olarak gösterilir
- ✅ **Son kullanım takibi**: Her doğrulama işleminde `last_used_at` güncellenir
- ✅ **Anahtar iptal etme**: Anahtarlar istendiğinde devre dışı bırakılabilir
- ✅ **Opsiyonel süre sonu**: Anahtarlar otomatik süre sonu ile oluşturulabilir
- ⚠️  **HTTPS kullanın**: Production ortamında her zaman HTTPS kullanın
- ⚠️  **API anahtarlarını loglamayın**: Anahtarları log dosyalarına yazmayın
- ⚠️  **Rate limiting**: Production için rate limiting uygulayın

## Dosya Yapısı

```
├── api_key_manager.py         # Ana API anahtar yönetim modülü
├── api_auth_middleware.py     # Kimlik doğrulama middleware'i
├── init_api_keys_db.py        # Veritabanı başlatma scripti
├── api_key_example.py         # Kullanım örnekleri
├── test_api_keys.py           # Birim testleri
└── API_KEY_MANAGEMENT.md      # Bu dokümantasyon
```

## API Referansı

### `api_key_manager.py`

#### `create_api_key(user_id, key_name, key_type='live', expires_days=None)`
Yeni bir API anahtarı oluşturur.

**Parametreler:**
- `user_id` (str): Kullanıcı kimliği
- `key_name` (str): Anahtar için açıklayıcı isim
- `key_type` (str): 'live' veya 'test' (varsayılan: 'live')
- `expires_days` (int, optional): Kaç gün sonra süresi dolacak

**Dönüş:** `(api_key, key_info)` tuple'ı veya hata durumunda `(None, None)`

#### `validate_api_key(api_key)`
Bir API anahtarını doğrular ve kullanıcı bilgilerini döndürür.

**Parametreler:**
- `api_key` (str): Doğrulanacak API anahtarı

**Dönüş:** Geçerliyse anahtar bilgileri dict'i, geçersizse `None`

#### `revoke_api_key(key_id, user_id)`
Bir API anahtarını iptal eder (devre dışı bırakır).

**Parametreler:**
- `key_id` (int): Anahtar ID'si
- `user_id` (str): Kullanıcı ID'si (yetkilendirme için)

**Dönüş:** Başarılıysa `True`, değilse `False`

#### `delete_api_key(key_id, user_id)`
Bir API anahtarını kalıcı olarak siler.

**Parametreler:**
- `key_id` (int): Anahtar ID'si
- `user_id` (str): Kullanıcı ID'si (yetkilendirme için)

**Dönüş:** Başarılıysa `True`, değilse `False`

#### `list_user_api_keys(user_id)`
Bir kullanıcının tüm API anahtarlarını listeler.

**Parametreler:**
- `user_id` (str): Kullanıcı ID'si

**Dönüş:** Anahtar bilgilerini içeren dict listesi

#### `get_api_key_info(key_id, user_id)`
Belirli bir API anahtarı hakkında bilgi alır.

**Parametreler:**
- `key_id` (int): Anahtar ID'si
- `user_id` (str): Kullanıcı ID'si (yetkilendirme için)

**Dönüş:** Anahtar bilgileri dict'i veya bulunamazsa `None`

### `api_auth_middleware.py`

#### `authenticate_api_request(authorization_header)`
Bir API isteğini Authorization header'ı kullanarak doğrular.

**Parametreler:**
- `authorization_header` (str): "Bearer <api_key>" formatında header değeri

**Dönüş:** Doğrulanmışsa auth context dict'i, değilse `None`

#### `check_api_auth(authorization_header)`
Kimlik doğrulama durumunu ve context'i döndürür.

**Parametreler:**
- `authorization_header` (str): Authorization header değeri

**Dönüş:** `(is_authenticated: bool, context: dict)` tuple'ı

## Sorun Giderme

### "Database error: file is not a database"
Veritabanı dosyası bozuk olabilir. Yeni bir veritabanı oluşturun:

```bash
python3 init_api_keys_db.py
```

### API anahtarı doğrulaması başarısız oluyor
- Anahtarın tam olarak kopyalandığından emin olun (boşluk yok)
- Anahtarın iptal edilmediğini kontrol edin
- Süre sonu tarihini kontrol edin

### Test hataları
Test veritabanı dosyalarını temizleyin:

```bash
rm -f test_api_keys*.db
python3 test_api_keys.py
```

## Lisans

Bu proje borctakip uygulamasının bir parçasıdır.

## Destek

Sorunlar veya sorular için GitHub issues kullanın.
