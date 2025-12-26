# API Anahtar Sistemi Nasıl Kullanılır?

Bu rehber, API anahtar sistemini nasıl kullanacağınızı adım adım gösterir.

## 📝 Adım 1: Veritabanını Hazırlama

İlk önce veritabanını hazırlayın:

```bash
python3 init_api_keys_db.py
```

Bu komut `api_keys` tablosunu veritabanınıza ekler. Çıktı şöyle olacak:

```
✓ API keys table initialized successfully in debt_database
Database schema is ready for API key management!
```

## 🔑 Adım 2: İlk API Anahtarınızı Oluşturma

Yeni bir Python dosyası oluşturun (örneğin `test_api.py`):

```python
from api_key_manager import create_api_key

# Yeni bir API anahtarı oluştur
api_key, key_info = create_api_key(
    user_id="kullanici123",      # Kullanıcı ID'niz
    key_name="Mobil Uygulama"    # Anahtara bir isim verin
)

if api_key:
    print(f"✅ API Anahtarınız: {api_key}")
    print(f"⚠️  Bu anahtarı güvenli bir yerde saklayın!")
    print(f"⚠️  Bir daha göremeyeceksiniz!")
else:
    print("❌ Anahtar oluşturulamadı")
```

Çalıştırın:

```bash
python3 test_api.py
```

Çıktı şöyle olacak:

```
✅ API Anahtarınız: sk_live_xYz123AbC456DeF789...
⚠️  Bu anahtarı güvenli bir yerde saklayın!
⚠️  Bir daha göremeyeceksiniz!
```

**ÖNEMLİ:** Bu anahtarı bir yere kaydedin (metin dosyası, şifre yöneticisi vb.). Bir daha göremezsiniz!

## 🔍 Adım 3: API Anahtarını Doğrulama

Bir kullanıcının anahtarının geçerli olup olmadığını kontrol edin:

```python
from api_key_manager import validate_api_key

# Kullanıcının gönderdiği anahtarı doğrula
api_key = "sk_live_xYz123AbC456DeF789..."  # Kullanıcıdan gelen anahtar

key_data = validate_api_key(api_key)

if key_data:
    print(f"✅ Geçerli anahtar!")
    print(f"   Kullanıcı ID: {key_data['user_id']}")
    print(f"   Anahtar Adı: {key_data['key_name']}")
else:
    print("❌ Geçersiz anahtar!")
```

## 🌐 Adım 4: Web API'nizde Kullanma

### Flask ile Kullanım

```python
from flask import Flask, request, jsonify
from api_auth_middleware import authenticate_api_request

app = Flask(__name__)

@app.route('/api/verim')
def get_data():
    # Authorization header'ını al
    auth_header = request.headers.get('Authorization')
    
    # Doğrula
    auth_context = authenticate_api_request(auth_header)
    
    if not auth_context:
        return jsonify({"error": "Yetkisiz erişim"}), 401
    
    # Kullanıcı kimliği doğrulandı
    user_id = auth_context['user_id']
    
    return jsonify({
        "message": "Merhaba!",
        "user_id": user_id,
        "data": "İşte verileriniz..."
    })

if __name__ == '__main__':
    app.run()
```

İstemci (client) tarafında kullanım:

```python
import requests

api_key = "sk_live_xYz123AbC456DeF789..."

response = requests.get(
    'http://localhost:5000/api/verim',
    headers={
        'Authorization': f'Bearer {api_key}'
    }
)

print(response.json())
```

### FastAPI ile Kullanım

```python
from fastapi import FastAPI, Header, HTTPException
from api_auth_middleware import authenticate_api_request

app = FastAPI()

@app.get("/api/verim")
def get_data(authorization: str = Header(None)):
    # Doğrula
    auth_context = authenticate_api_request(authorization)
    
    if not auth_context:
        raise HTTPException(status_code=401, detail="Yetkisiz erişim")
    
    # Kullanıcı kimliği doğrulandı
    user_id = auth_context['user_id']
    
    return {
        "message": "Merhaba!",
        "user_id": user_id,
        "data": "İşte verileriniz..."
    }
```

## 📋 Adım 5: Anahtarları Listeleme

Bir kullanıcının tüm anahtarlarını görmek için:

```python
from api_key_manager import list_user_api_keys

user_id = "kullanici123"
keys = list_user_api_keys(user_id)

print(f"Toplam {len(keys)} anahtar:")
for key in keys:
    durum = "🟢 Aktif" if key['is_active'] else "🔴 Pasif"
    print(f"  • {key['key_name']}")
    print(f"    Durum: {durum}")
    print(f"    Ön ek: {key['key_prefix']}")
    print(f"    Oluşturma: {key['created_at']}")
    if key['last_used_at']:
        print(f"    Son Kullanım: {key['last_used_at']}")
    print()
```

## 🚫 Adım 6: Anahtarı İptal Etme

Bir anahtarı devre dışı bırakmak için:

```python
from api_key_manager import revoke_api_key

# Anahtar ID'si ve kullanıcı ID'si gerekli
success = revoke_api_key(
    key_id=1,              # Anahtarın ID'si
    user_id="kullanici123" # Kullanıcının ID'si
)

if success:
    print("✅ Anahtar iptal edildi!")
else:
    print("❌ İptal edilemedi")
```

## 🗑️ Adım 7: Anahtarı Silme

Bir anahtarı kalıcı olarak silmek için:

```python
from api_key_manager import delete_api_key

success = delete_api_key(
    key_id=1,
    user_id="kullanici123"
)

if success:
    print("✅ Anahtar silindi!")
else:
    print("❌ Silinemedi")
```

## 🔐 Test Anahtarı Oluşturma

Test ortamı için geçici bir anahtar oluşturun:

```python
from api_key_manager import create_api_key

# 30 gün sonra süresi dolacak test anahtarı
api_key, key_info = create_api_key(
    user_id="kullanici123",
    key_name="Test Anahtarı",
    key_type="test",        # "test" tipi
    expires_days=30         # 30 gün sonra sona erer
)

print(f"Test Anahtarı: {api_key}")
print(f"Son Kullanma: {key_info['expires_at']}")
```

Test anahtarları `sk_test_` ile başlar, canlı anahtarlar `sk_live_` ile başlar.

## 📱 Örnek: Komple Mobil Uygulama Senaryosu

### 1. Kullanıcı Kaydı Sırasında Anahtar Oluşturma

```python
from api_key_manager import create_api_key

def register_user(username, email, password):
    # ... kullanıcı kaydı işlemleri ...
    user_id = "12345"  # Yeni kullanıcının ID'si
    
    # Otomatik olarak bir API anahtarı oluştur
    api_key, key_info = create_api_key(
        user_id=user_id,
        key_name=f"{username}'in Anahtarı"
    )
    
    # Anahtarı kullanıcıya göster (sadece bir kez!)
    return {
        "user_id": user_id,
        "api_key": api_key,
        "message": "Bu anahtarı kaydedin!"
    }
```

### 2. Mobil Uygulamada Anahtarı Saklama

Mobil uygulamanızda anahtarı güvenli bir şekilde saklayın:

- iOS: Keychain kullanın
- Android: SharedPreferences (encrypted) kullanın

### 3. Her API İsteğinde Gönderme

```python
import requests

API_BASE_URL = "https://api.example.com"
API_KEY = "sk_live_xYz123..."  # Güvenli depodan alınan anahtar

def get_transactions():
    response = requests.get(
        f"{API_BASE_URL}/api/transactions",
        headers={'Authorization': f'Bearer {API_KEY}'}
    )
    return response.json()

def create_transaction(data):
    response = requests.post(
        f"{API_BASE_URL}/api/transactions",
        headers={'Authorization': f'Bearer {API_KEY}'},
        json=data
    )
    return response.json()
```

### 4. Sunucu Tarafında Doğrulama

```python
from flask import Flask, request, jsonify
from api_auth_middleware import authenticate_api_request

app = Flask(__name__)

def require_auth(f):
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_context = authenticate_api_request(auth_header)
        
        if not auth_context:
            return jsonify({"error": "Yetkisiz"}), 401
        
        # auth_context'i fonksiyona ekle
        return f(auth_context, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/transactions', methods=['GET'])
@require_auth
def get_transactions(auth_context):
    user_id = auth_context['user_id']
    
    # Kullanıcının işlemlerini getir
    transactions = get_user_transactions(user_id)
    
    return jsonify({"transactions": transactions})

@app.route('/api/transactions', methods=['POST'])
@require_auth
def create_transaction(auth_context):
    user_id = auth_context['user_id']
    data = request.get_json()
    
    # Yeni işlem oluştur
    transaction = create_user_transaction(user_id, data)
    
    return jsonify({"transaction": transaction})
```

## 🧪 Test Etme

Tüm özellikleri test etmek için örnek scripti çalıştırın:

```bash
python3 api_key_example.py
```

Veya birim testleri çalıştırın:

```bash
python3 test_api_keys.py
```

## ❓ Sık Sorulan Sorular

### API anahtarımı kaybettim, nasıl bulabilirim?

Bulamazsınız. API anahtarları sadece oluşturulurken bir kez gösterilir ve hash'lenerek saklanır. Yeni bir anahtar oluşturmanız gerekir.

### Birden fazla anahtar oluşturabilir miyim?

Evet! Her kullanıcı istediği kadar anahtar oluşturabilir. Örneğin:
- Mobil uygulama için bir anahtar
- Web sitesi için bir anahtar
- Test için bir anahtar

### Anahtarım çalınırsa ne yaparım?

Hemen `revoke_api_key()` fonksiyonu ile anahtarı iptal edin. Çalınan anahtar artık kullanılamaz.

### Test ve canlı anahtarlar arasındaki fark nedir?

- **Canlı anahtarlar** (`sk_live_`): Gerçek üretim ortamı için
- **Test anahtarlar** (`sk_test_`): Test ve geliştirme ortamı için

İkisi de aynı şekilde çalışır, sadece isimlendirilmesi farklıdır.

### API anahtarları güvenli mi?

Evet! Anahtarlar:
- SHA-256 ile hash'lenerek saklanır
- Asla düz metin olarak saklanmaz
- Sadece oluşturulurken bir kez gösterilir
- Her kullanım kaydedilir

### Anahtarların süresi dolabilir mi?

Evet, isterseniz. `expires_days` parametresi ile:

```python
create_api_key(user_id, key_name, expires_days=30)  # 30 gün sonra sona erer
```

## 🆘 Yardım

Daha fazla bilgi için:
- `API_KEY_MANAGEMENT.md` - Detaylı dokümantasyon
- `api_key_example.py` - Tam örnek kod
- `test_api_keys.py` - Test örnekleri

Sorun mu yaşıyorsunuz? GitHub Issues'da bildirin!
