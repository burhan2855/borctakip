# 🚀 Hızlı Başlangıç Kartı - Quick Start Card

## 📖 Hangi dosyayı okumalıyım? / Which file should I read?

```
┌─────────────────────────────────────────────────────────────┐
│  NE YAPMAK İSTİYORSUN?          │  HANGİ DOSYA?            │
│  WHAT DO YOU WANT?               │  WHICH FILE?             │
├─────────────────────────────────────────────────────────────┤
│  🇹🇷 Türkçe adım adım rehber     │  NASIL_KULLANILIR.md     │
│     Turkish step-by-step         │                          │
│                                  │                          │
│  📱 Android'de nasıl kullanırım? │  ANDROID_KULLANIMI.md    │
│     How to use in Android?       │                          │
│                                  │                          │
│  🌍 English full documentation   │  API_KEY_MANAGEMENT.md   │
│                                  │                          │
│  ⚡ Hızlı genel bakış            │  README.md               │
│     Quick overview               │                          │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 3 Dakikada Başla / Start in 3 Minutes

### 1️⃣ Veritabanını Hazırla / Setup Database
```bash
python3 init_api_keys_db.py
```

### 2️⃣ İlk Örneği Çalıştır / Run First Example
```bash
python3 basit_ornek.py
```

Bu size gösterecek / This will show you:
- ✅ Nasıl API anahtarı oluşturulur / How to create API key
- ✅ Nasıl doğrulanır / How to validate
- ✅ Nasıl kullanılır / How to use

### 3️⃣ Kendi Kodunuzda Kullanın / Use in Your Code

**Python'da / In Python:**
```python
from api_key_manager import create_api_key, validate_api_key

# Anahtar oluştur / Create key
api_key, info = create_api_key('user123', 'Mobil App')
print(f"Anahtarınız / Your key: {api_key}")

# Doğrula / Validate
if validate_api_key(api_key):
    print("Geçerli! / Valid!")
```

**Android'de / In Android:**
```kotlin
// 1. API anahtarını güvenli şekilde sakla
ApiKeyManager(context).saveApiKey(apiKey, userId)

// 2. Retrofit ile kullan
RetrofitClient.setApiKey(apiKey)
val transactions = apiService.getTransactions()
```

## 🏗️ Mimari / Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   ANDROID UYGULAMANIZ                     │
│                   YOUR ANDROID APP                        │
│                                                           │
│  • Retrofit HTTP Client                                  │
│  • Authorization: Bearer sk_live_xxx                     │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ HTTP İstekleri / HTTP Requests
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              PYTHON BACKEND SERVER                        │
│              (server.py - Flask)                         │
│                                                           │
│  ┌────────────────────────────────────────────────┐     │
│  │  api_auth_middleware.py                        │     │
│  │  • Authorization header kontrol                │     │
│  │  • API anahtarını doğrula                      │     │
│  │  • Kullanıcı bilgilerini döndür               │     │
│  └────────────────────────────────────────────────┘     │
│                     │                                     │
│                     ▼                                     │
│  ┌────────────────────────────────────────────────┐     │
│  │  api_key_manager.py                            │     │
│  │  • SHA-256 hash ile karşılaştır               │     │
│  │  • Son kullanım zamanını güncelle             │     │
│  │  • Süre sonu kontrolü                          │     │
│  └────────────────────────────────────────────────┘     │
│                     │                                     │
│                     ▼                                     │
│  ┌────────────────────────────────────────────────┐     │
│  │  debt_database (SQLite)                        │     │
│  │  • api_keys tablosu                            │     │
│  │  • transactions tablosu                        │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

## 📱 Android Studio İçin Hızlı Adımlar / Quick Steps for Android Studio

### 1. Backend Server'ı Başlat / Start Backend Server
```bash
cd /path/to/borctakip
python3 server.py
```
✅ Server çalışıyor: `http://localhost:5000`

### 2. API Anahtarı Oluştur / Create API Key
```bash
python3 -c "
from api_key_manager import create_api_key
k, i = create_api_key('android_user', 'My Android App')
print(f'API Anahtarı / API Key: {k}')
"
```
✅ Anahtarı kopyala ve sakla / Copy and save the key

### 3. Android Projenize Ekleyin / Add to Android Project

**Gradle dependencies:**
```gradle
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
implementation 'androidx.security:security-crypto:1.1.0-alpha06'
```

**Retrofit Client:**
```kotlin
object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:5000/"  // Emulator
    
    fun setApiKey(key: String) {
        // Authorization header'a ekle
    }
}
```

### 4. Detaylı Kotlin Kodu İçin / For Detailed Kotlin Code
👉 `ANDROID_KULLANIMI.md` dosyasını okuyun

## ❓ Sık Sorulan Sorular / FAQ

**Soru:** API anahtarım çalışmıyor / My API key doesn't work
**Cevap:** 
1. Server çalışıyor mu? / Is server running?
2. Anahtar doğru kopyalandı mı? / Is key copied correctly?
3. `sk_live_` veya `sk_test_` ile başlıyor mu? / Starts with prefix?

**Soru:** Android'den bağlanamıyorum / Can't connect from Android
**Cevap:**
- Emulator: `http://10.0.2.2:5000` kullan
- Gerçek cihaz: Bilgisayar IP'si kullan (ör: `http://192.168.1.5:5000`)
- Aynı WiFi ağında olmalısınız / Must be on same WiFi

**Soru:** Hangi endpoint'ler var? / What endpoints exist?
**Cevap:**
```
GET  /api/transactions       - Tüm işlemler / All transactions
POST /api/transactions       - Yeni işlem / New transaction
GET  /api/user/info         - Kullanıcı bilgisi / User info
GET  /api/user/keys         - API anahtarları / API keys
GET  /health                - Sağlık kontrolü / Health check
```

## 🎓 Daha Fazla Bilgi / More Information

| Konu / Topic | Dosya / File |
|--------------|--------------|
| Temel kullanım / Basic usage | `basit_ornek.py` |
| Tam Python örneği / Full Python example | `api_key_example.py` |
| Android entegrasyonu / Android integration | `ANDROID_KULLANIMI.md` |
| Adım adım Türkçe / Step by step Turkish | `NASIL_KULLANILIR.md` |
| İngilizce doküman / English docs | `API_KEY_MANAGEMENT.md` |
| API server kodu / API server code | `server.py` |

## ✅ Test Et / Test It

```bash
# Testleri çalıştır / Run tests
python3 test_api_keys.py

# Gereksinimleri doğrula / Verify requirements
python3 verify_requirements.py

# Basit örnek / Simple example
python3 basit_ornek.py

# Server'ı başlat / Start server
python3 server.py
```

## 💡 İpuçları / Tips

1. **Geliştirme / Development:** Test anahtarı kullan (`sk_test_`)
2. **Production:** Canlı anahtar kullan (`sk_live_`)
3. **Güvenlik / Security:** API anahtarını asla loglamayın / Never log API keys
4. **Android:** EncryptedSharedPreferences kullanın / Use EncryptedSharedPreferences
5. **Server:** HTTPS kullanın production'da / Use HTTPS in production

## 🆘 Yardım / Help

- 📖 Dokümantasyon okuyun / Read documentation
- ✅ Testleri çalıştırın / Run tests
- 🐛 Hata bulursanız / If you find bugs: GitHub Issues

---

**Başarılar! / Good luck! 🚀**
