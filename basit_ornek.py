#!/usr/bin/env python3
"""
Basit Kullanım Örneği - Simple Usage Example
Bu script API anahtar sisteminin en yaygın kullanımını gösterir.
This script demonstrates the most common usage of the API key system.
"""

from api_key_manager import (
    create_api_key, 
    validate_api_key, 
    list_user_api_keys
)
from api_auth_middleware import authenticate_api_request
from init_api_keys_db import init_api_keys_table


def main():
    print("\n" + "="*60)
    print("  BASİT KULLANIM ÖRNEĞİ - SIMPLE USAGE EXAMPLE")
    print("="*60)
    
    # Adım 1: Veritabanını hazırla
    print("\n📁 Adım 1: Veritabanı hazırlanıyor...")
    print("   Step 1: Initializing database...")
    init_api_keys_table('debt_database')
    
    # Adım 2: Yeni bir API anahtarı oluştur
    print("\n🔑 Adım 2: Yeni API anahtarı oluşturuluyor...")
    print("   Step 2: Creating new API key...")
    
    api_key, key_info = create_api_key(
        user_id="ornek_kullanici",
        key_name="Benim İlk Anahtarım"
    )
    
    if not api_key:
        print("❌ Anahtar oluşturulamadı!")
        print("   Could not create key!")
        return
    
    print(f"\n✅ API Anahtarınız oluşturuldu!")
    print(f"   Your API key has been created!")
    print(f"\n   🔐 API Anahtarı / API Key:")
    print(f"   {api_key}")
    print(f"\n   📝 Anahtar Bilgileri / Key Info:")
    print(f"   • ID: {key_info['id']}")
    print(f"   • İsim / Name: {key_info['key_name']}")
    print(f"   • Ön Ek / Prefix: {key_info['key_prefix']}")
    print(f"   • Oluşturma / Created: {key_info['created_at']}")
    print(f"\n   ⚠️  ÖNEMLİ / IMPORTANT:")
    print(f"   Bu anahtarı güvenli bir yerde saklayın!")
    print(f"   Save this key in a secure location!")
    print(f"   Bir daha göremeyeceksiniz!")
    print(f"   You won't be able to see it again!")
    
    # Adım 3: Anahtarı doğrula
    print("\n🔍 Adım 3: Anahtar doğrulanıyor...")
    print("   Step 3: Validating key...")
    
    key_data = validate_api_key(api_key)
    
    if key_data:
        print(f"\n✅ Anahtar geçerli! / Key is valid!")
        print(f"   • Kullanıcı ID / User ID: {key_data['user_id']}")
        print(f"   • Son Kullanım / Last Used: {key_data['last_used_at']}")
    else:
        print("\n❌ Anahtar geçersiz! / Key is invalid!")
    
    # Adım 4: HTTP Authorization header ile doğrulama
    print("\n🌐 Adım 4: HTTP Authorization ile doğrulama...")
    print("   Step 4: Validating with HTTP Authorization...")
    
    auth_header = f"Bearer {api_key}"
    print(f"\n   Authorization: {auth_header[:50]}...")
    
    auth_context = authenticate_api_request(auth_header)
    
    if auth_context:
        print(f"\n✅ Kimlik doğrulandı! / Authenticated!")
        print(f"   • Kullanıcı ID / User ID: {auth_context['user_id']}")
        print(f"   • Anahtar Adı / Key Name: {auth_context['key_name']}")
    else:
        print("\n❌ Kimlik doğrulanamadı! / Authentication failed!")
    
    # Adım 5: Kullanıcının tüm anahtarlarını listele
    print("\n📋 Adım 5: Tüm anahtarlar listeleniyor...")
    print("   Step 5: Listing all keys...")
    
    keys = list_user_api_keys("ornek_kullanici")
    
    print(f"\n   Toplam / Total: {len(keys)} anahtar / key(s)")
    for i, key in enumerate(keys, 1):
        status = "🟢 Aktif / Active" if key['is_active'] else "🔴 Pasif / Inactive"
        print(f"\n   {i}. {key['key_name']}")
        print(f"      Durum / Status: {status}")
        print(f"      Ön Ek / Prefix: {key['key_prefix']}")
        print(f"      Oluşturma / Created: {key['created_at']}")
    
    # Kullanım örnekleri
    print("\n" + "="*60)
    print("  KULLANIM ÖRNEKLERİ - USAGE EXAMPLES")
    print("="*60)
    
    print("\n📱 Flask ile / With Flask:")
    print("""
    from flask import Flask, request, jsonify
    from api_auth_middleware import authenticate_api_request
    
    app = Flask(__name__)
    
    @app.route('/api/data')
    def get_data():
        auth = request.headers.get('Authorization')
        auth_context = authenticate_api_request(auth)
        
        if not auth_context:
            return jsonify({"error": "Unauthorized"}), 401
        
        return jsonify({"user_id": auth_context['user_id']})
    """)
    
    print("\n🐍 Python İstemci / Python Client:")
    print(f"""
    import requests
    
    api_key = "{api_key[:30]}..."
    
    response = requests.get(
        'http://localhost:5000/api/data',
        headers={{'Authorization': f'Bearer {{api_key}}'}}
    )
    
    print(response.json())
    """)
    
    print("\n💡 Daha fazla örnek için / For more examples:")
    print("   • NASIL_KULLANILIR.md - Detaylı rehber / Detailed guide")
    print("   • api_key_example.py - Tam örnekler / Complete examples")
    print("   • API_KEY_MANAGEMENT.md - API dokümantasyonu / API docs")
    
    print("\n" + "="*60)
    print("  ✅ TAMAMLANDI - COMPLETED")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
