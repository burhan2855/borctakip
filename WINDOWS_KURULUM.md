# Windows Kurulum Rehberi - Windows Installation Guide

Bu rehber, API anahtar sistemini Windows'ta nasıl kullanacağınızı gösterir.

## 📋 Gereksinimler / Requirements

- Windows 10 veya üzeri
- Python 3.8 veya üzeri

## 🔧 Python Kurulumu / Python Installation

### Adım 1: Python'un Yüklü Olup Olmadığını Kontrol Edin

Windows PowerShell veya Command Prompt'u açın ve şu komutu çalıştırın:

```cmd
python --version
```

veya

```cmd
py --version
```

Eğer bir versiyon numarası görüyorsanız (örn: `Python 3.12.0`), Python yüklüdür. **Adım 2'yi atlayın.**

### Adım 2: Python'u Yükleyin (Eğer Yüklü Değilse)

1. **Python'u indirin:**
   - [https://www.python.org/downloads/](https://www.python.org/downloads/) adresine gidin
   - "Download Python" butonuna tıklayın
   - İndirilen `.exe` dosyasını çalıştırın

2. **Kurulum sırasında önemli:**
   - ✅ **"Add Python to PATH"** seçeneğini işaretleyin (çok önemli!)
   - "Install Now" seçeneğine tıklayın

3. **Kurulumu doğrulayın:**
   - Yeni bir Command Prompt penceresi açın
   - `python --version` komutunu çalıştırın

## 🚀 API Anahtar Sistemini Kullanma

### Adım 1: Proje Dizinine Gidin

```cmd
cd "C:\Users\burha\Desktop\uygulama yedek\Borç Takip Pro\BorcTakip-5"
```

**Not:** Dizin adınız farklıysa, kendi dizin yolunuzu yazın.

### Adım 2: Veritabanını Hazırlayın

```cmd
python init_api_keys_db.py
```

Çıktı:
```
✓ API keys table initialized successfully in debt_database
Database schema is ready for API key management!
```

### Adım 3: Basit Örneği Çalıştırın

```cmd
python basit_ornek.py
```

Bu komut size API anahtar sisteminin nasıl çalıştığını gösterecek.

### Adım 4: API Server'ı Başlatın (Android için)

```cmd
python server.py
```

Server başladığında şöyle bir çıktı göreceksiniz:
```
============================================================
  🚀 Borç Takip API Server Başlatılıyor...
============================================================

📍 Server: http://localhost:5000
📍 Android Emulator için: http://10.0.2.2:5000
```

**Önemli:** Server çalışırken bu pencereyi kapatmayın!

## 🔑 API Anahtarı Oluşturma

### Yöntem 1: Basit Örnek ile

```cmd
python basit_ornek.py
```

Script çalıştığında size bir API anahtarı oluşturacak ve gösterecek.

### Yöntem 2: Manuel Olarak

```cmd
python -c "from api_key_manager import create_api_key; k, i = create_api_key('user123', 'Windows App'); print(f'API Anahtarı: {k}')"
```

**⚠️ Önemli:** API anahtarını bir yere kaydedin! Bir daha göremezsiniz.

## 📱 Android Studio ile Kullanım

### Adım 1: Server'ı Başlatın

Bir Command Prompt penceresinde:

```cmd
cd "C:\Users\burha\Desktop\uygulama yedek\Borç Takip Pro\BorcTakip-5"
python server.py
```

Bu pencereyi açık bırakın!

### Adım 2: Android Studio'yu Açın

1. Android Studio'yu açın
2. Projenizi açın
3. `ANDROID_KULLANIMI.md` dosyasındaki Kotlin kodunu projenize ekleyin

### Adım 3: Retrofit'i Yapılandırın

`RetrofitClient.kt` içinde base URL'i ayarlayın:

```kotlin
// Emulator kullanıyorsanız:
private const val BASE_URL = "http://10.0.2.2:5000/"

// Gerçek cihaz kullanıyorsanız:
// Bilgisayarınızın IP adresini bulun (cmd'de: ipconfig)
// Örnek: private const val BASE_URL = "http://192.168.1.100:5000/"
```

### Adım 4: API Anahtarını Kullanın

1. Adım 1'de oluşturduğunuz API anahtarını Android uygulamanıza girin
2. Uygulamayı çalıştırın
3. Server loglarını kontrol edin

## 🧪 Test Etme

### Tüm Testleri Çalıştırın

```cmd
python test_api_keys.py
```

Çıktı:
```
Ran 29 tests in 0.5s
OK
```

### Basit Test

```cmd
python -c "print('Python çalışıyor!')"
```

## ❌ Sorun Giderme / Troubleshooting

### "python is not recognized"

**Çözüm 1: py launcher kullanın**
```cmd
py init_api_keys_db.py
py basit_ornek.py
py server.py
```

**Çözüm 2: Python'u PATH'e ekleyin**

1. Windows Arama'ya "environment" yazın
2. "Edit the system environment variables" seçin
3. "Environment Variables" butonuna tıklayın
4. "Path" seçin ve "Edit" tıklayın
5. "New" tıklayın ve Python kurulum yolunu ekleyin:
   - `C:\Python312\` (veya Python'un yüklü olduğu yer)
   - `C:\Python312\Scripts\`
6. "OK" ile kaydedin
7. **Yeni bir Command Prompt penceresi açın**

**Çözüm 3: Tam yol ile çalıştırın**
```cmd
C:\Python312\python.exe init_api_keys_db.py
```

### "No module named 'flask'"

Flask yüklü değil. Yükleyin:

```cmd
python -m pip install flask
```

veya

```cmd
py -m pip install flask
```

### "Address already in use" (Port 5000 kullanımda)

Başka bir program 5000 portunu kullanıyor. Server'ı farklı bir portta başlatın:

```cmd
python server.py
```

Sonra `server.py` dosyasını düzenleyin, `port=5000` satırını `port=5001` yapın.

### Android Emulator'dan bağlanamıyorum

1. **Server çalışıyor mu kontrol edin:**
   ```cmd
   curl http://localhost:5000/health
   ```

2. **Windows Firewall'u kontrol edin:**
   - Windows Güvenlik'i açın
   - "Firewall & network protection" seçin
   - Python'a izin verin

3. **Emulator için doğru URL kullanın:**
   - `http://10.0.2.2:5000` (localhost DEĞİL!)

### Gerçek Android cihazdan bağlanamıyorum

1. **Bilgisayarınızın IP adresini bulun:**
   ```cmd
   ipconfig
   ```
   
   `IPv4 Address` satırını bulun (örn: `192.168.1.100`)

2. **Aynı WiFi ağında olduğunuzdan emin olun:**
   - Bilgisayar ve telefon aynı WiFi'ye bağlı olmalı

3. **Android'de URL'i değiştirin:**
   ```kotlin
   private const val BASE_URL = "http://192.168.1.100:5000/"
   ```

## 📚 Daha Fazla Bilgi

- **Adım adım Türkçe rehber:** `NASIL_KULLANILIR.md`
- **Android entegrasyonu:** `ANDROID_KULLANIMI.md`
- **Hızlı başlangıç:** `HIZLI_BASLANGIC.md`
- **İngilizce doküman:** `API_KEY_MANAGEMENT.md`

## 💡 İpuçları

1. **Command Prompt vs PowerShell:**
   - Her ikisi de çalışır
   - PowerShell'de `python` yerine `python.exe` da kullanabilirsiniz

2. **Dizin adlarında boşluk varsa:**
   ```cmd
   cd "C:\Dizin İçinde Boşluk Var\proje"
   ```
   Tırnak işaretleri kullanın!

3. **Script'leri düzenlemek için:**
   - Notepad++, VS Code veya başka bir metin editörü kullanın
   - Notepad (Windows'un varsayılan not defteri) önerilmez

4. **Server'ı arka planda çalıştırmak için:**
   ```cmd
   start /B python server.py
   ```

## ✅ Başarıyla Kuruldu mu Kontrol Edin

Aşağıdaki komutlar hata vermeden çalışmalı:

```cmd
REM Python versiyonu
python --version

REM Veritabanı hazırlama
python init_api_keys_db.py

REM Basit örnek
python basit_ornek.py

REM Testler
python test_api_keys.py
```

Hepsi çalışıyorsa, kurulum başarılı! 🎉

## 🆘 Hala Sorun mu Var?

1. Python'un doğru kurulduğundan emin olun
2. Command Prompt'u **yönetici olarak** çalıştırın
3. Antivirüs yazılımınızı geçici olarak devre dışı bırakın
4. Bilgisayarı yeniden başlatın ve tekrar deneyin

---

**Windows kullanıcıları için hazırlandı** 🪟
