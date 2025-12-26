# borctakip

Borç takip uygulaması - Debt tracking application

## Özellikler / Features

- Borç ve alacak takibi / Debt and credit tracking
- İşlem geçmişi / Transaction history
- Kısmi ödemeler / Partial payments
- **API Anahtar Yönetimi** / **API Key Management** ✨ Yeni!

## API Anahtar Yönetimi / API Key Management

Bu uygulama artık kullanıcıların kendi API anahtarlarını oluşturup yönetebilmeleri için kapsamlı bir API anahtar yönetim sistemi içermektedir.

This application now includes a comprehensive API key management system that allows users to create and manage their own API keys.

### 🚀 Hızlı Başlangıç / Quick Start

**Türkçe Rehber:** Adım adım kullanım için → [NASIL_KULLANILIR.md](NASIL_KULLANILIR.md) 📖

**English Guide:** For detailed usage → [API_KEY_MANAGEMENT.md](API_KEY_MANAGEMENT.md) 📖

```bash
# 1. Veritabanını başlat / Initialize database
python3 init_api_keys_db.py

# 2. Basit örneği çalıştır / Run simple example
python3 basit_ornek.py

# 3. Tam örneği gör / See complete example
python3 api_key_example.py

# 4. Testleri çalıştır / Run tests
python3 test_api_keys.py
```

### Özellikler / Features

- ✅ Güvenli API anahtarı üretimi / Secure API key generation
- ✅ SHA-256 hash ile güvenli saklama / Secure storage with SHA-256 hash
- ✅ Bearer token authentication
- ✅ Anahtar iptal etme / Key revocation
- ✅ Son kullanım takibi / Last usage tracking
- ✅ Opsiyonel süre sonu / Optional expiration

### 📚 Dokümantasyon / Documentation

**Türkçe:**
- [NASIL_KULLANILIR.md](NASIL_KULLANILIR.md) - Adım adım kullanım rehberi
- [basit_ornek.py](basit_ornek.py) - Basit örnek kod

**English:**
- [API_KEY_MANAGEMENT.md](API_KEY_MANAGEMENT.md) - Complete API documentation
- [api_key_example.py](api_key_example.py) - Full example code

### Güvenlik / Security

- API anahtarları asla düz metin olarak saklanmaz / API keys are never stored in plaintext
- SHA-256 hash kullanılır / SHA-256 hashing is used
- Anahtarlar sadece oluşturma sırasında gösterilir / Keys are shown only once during creation
- Production'da HTTPS zorunludur / HTTPS is required in production