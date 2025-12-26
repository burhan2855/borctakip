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

### Hızlı Başlangıç / Quick Start

```bash
# Veritabanını başlat / Initialize database
python3 init_api_keys_db.py

# Örnek kullanımı gör / See example usage
python3 api_key_example.py

# Testleri çalıştır / Run tests
python3 test_api_keys.py
```

### Özellikler / Features

- ✅ Güvenli API anahtarı üretimi / Secure API key generation
- ✅ SHA-256 hash ile güvenli saklama / Secure storage with SHA-256 hash
- ✅ Bearer token authentication
- ✅ Anahtar iptal etme / Key revocation
- ✅ Son kullanım takibi / Last usage tracking
- ✅ Opsiyonel süre sonu / Optional expiration

### Dokümantasyon / Documentation

Detaylı kullanım için bkz. / For detailed usage, see: [API_KEY_MANAGEMENT.md](API_KEY_MANAGEMENT.md)

### Güvenlik / Security

- API anahtarları asla düz metin olarak saklanmaz / API keys are never stored in plaintext
- SHA-256 hash kullanılır / SHA-256 hashing is used
- Anahtarlar sadece oluşturma sırasında gösterilir / Keys are shown only once during creation
- Production'da HTTPS zorunludur / HTTPS is required in production