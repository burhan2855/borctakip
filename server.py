#!/usr/bin/env python3
"""
Flask API Server for Android Application
Bu server Android uygulamanızın backend'ı olarak çalışır.
"""

from flask import Flask, request, jsonify
from api_auth_middleware import authenticate_api_request
from api_key_manager import create_api_key, list_user_api_keys
import sqlite3
from datetime import datetime
import os
import logging

# Configuration
DB_PATH = os.environ.get('DB_PATH', 'debt_database')
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Allowed fields for transaction updates (whitelist for security)
ALLOWED_TRANSACTION_FIELDS = ['title', 'amount', 'isDebt', 'status', 'category', 'date']

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def require_auth(f):
    """Authentication decorator - Her korumalı endpoint için kullanılır"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_context = authenticate_api_request(auth_header)
        
        if not auth_context:
            return jsonify({
                "error": "Unauthorized",
                "message": "Geçersiz veya eksik API anahtarı"
            }), 401
        
        return f(auth_context, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function


# ============================================================================
# Transaction Endpoints (İşlem API'leri)
# ============================================================================

@app.route('/api/transactions', methods=['GET'])
@require_auth
def get_transactions(auth_context):
    """
    Kullanıcının tüm işlemlerini getir
    GET /api/transactions
    Headers: Authorization: Bearer <api_key>
    """
    user_id = auth_context['user_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, amount, isDebt, status, category, date 
            FROM transactions 
            WHERE userId = ?
            ORDER BY id DESC
        ''', (user_id,))
        
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "transactions": transactions,
            "count": len(transactions)
        })
    
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@require_auth
def get_transaction(auth_context, transaction_id):
    """
    Belirli bir işlemi getir
    GET /api/transactions/<id>
    """
    user_id = auth_context['user_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, amount, isDebt, status, category, date 
            FROM transactions 
            WHERE id = ? AND userId = ?
        ''', (transaction_id, user_id))
        
        transaction = cursor.fetchone()
        conn.close()
        
        if transaction:
            return jsonify({"transaction": dict(transaction)})
        else:
            return jsonify({"error": "Transaction not found"}), 404
    
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/transactions', methods=['POST'])
@require_auth
def create_transaction(auth_context):
    """
    Yeni işlem oluştur
    POST /api/transactions
    Body: {
        "title": "İşlem Adı",
        "amount": 100.50,
        "isDebt": true,
        "status": "pending",
        "category": "kategori",
        "date": "2025-12-26"
    }
    """
    user_id = auth_context['user_id']
    data = request.get_json()
    
    # Gerekli alanları kontrol et
    required_fields = ['title', 'amount', 'isDebt', 'status', 'category', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (userId, title, amount, isDebt, status, category, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, data['title'], data['amount'], data['isDebt'], 
              data['status'], data['category'], data['date']))
        
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "id": transaction_id,
            "message": "Transaction created successfully"
        }), 201
    
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@require_auth
def update_transaction(auth_context, transaction_id):
    """
    İşlemi güncelle
    PUT /api/transactions/<id>
    """
    user_id = auth_context['user_id']
    data = request.get_json()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Önce işlemin kullanıcıya ait olduğunu kontrol et
        cursor.execute('SELECT id FROM transactions WHERE id = ? AND userId = ?', 
                      (transaction_id, user_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Transaction not found"}), 404
        
        # Güncelleme sorgusu oluştur - whitelist ile güvenli
        update_fields = []
        update_values = []
        
        for field in ALLOWED_TRANSACTION_FIELDS:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])
        
        if not update_fields:
            conn.close()
            return jsonify({"error": "No fields to update"}), 400
        
        update_values.append(transaction_id)
        update_values.append(user_id)
        
        cursor.execute(f'''
            UPDATE transactions 
            SET {', '.join(update_fields)}
            WHERE id = ? AND userId = ?
        ''', update_values)
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Transaction updated successfully"})
    
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@require_auth
def delete_transaction(auth_context, transaction_id):
    """
    İşlemi sil
    DELETE /api/transactions/<id>
    """
    user_id = auth_context['user_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM transactions WHERE id = ? AND userId = ?', 
                      (transaction_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Transaction not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Transaction deleted successfully"})
    
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# API Key Management Endpoints (API Anahtar Yönetimi)
# ============================================================================

@app.route('/api/user/keys', methods=['GET'])
@require_auth
def get_user_keys(auth_context):
    """
    Kullanıcının API anahtarlarını listele
    GET /api/user/keys
    """
    user_id = auth_context['user_id']
    keys = list_user_api_keys(user_id)
    
    return jsonify({"keys": keys})


@app.route('/api/user/keys', methods=['POST'])
@require_auth
def create_user_key(auth_context):
    """
    Yeni API anahtarı oluştur
    POST /api/user/keys
    Body: {
        "key_name": "Yeni Cihaz"
    }
    """
    user_id = auth_context['user_id']
    data = request.get_json()
    key_name = data.get('key_name', 'Android App')
    
    api_key, key_info = create_api_key(user_id, key_name)
    
    if api_key:
        return jsonify({
            "api_key": api_key,
            "key_info": key_info,
            "message": "API key created successfully. Save it securely!"
        }), 201
    else:
        return jsonify({"error": "Could not create API key"}), 500


# ============================================================================
# User Info Endpoint (Kullanıcı Bilgisi)
# ============================================================================

@app.route('/api/user/info', methods=['GET'])
@require_auth
def get_user_info(auth_context):
    """
    Kullanıcı bilgilerini getir
    GET /api/user/info
    """
    return jsonify({
        "user_id": auth_context['user_id'],
        "key_name": auth_context['key_name'],
        "authenticated": auth_context['authenticated']
    })


# ============================================================================
# Health Check (Sağlık Kontrolü)
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Server sağlık kontrolü - Authentication gerektirmez
    GET /health
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """Ana sayfa"""
    return jsonify({
        "message": "Borç Takip API Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "transactions": {
                "list": "GET /api/transactions",
                "get": "GET /api/transactions/<id>",
                "create": "POST /api/transactions",
                "update": "PUT /api/transactions/<id>",
                "delete": "DELETE /api/transactions/<id>"
            },
            "keys": {
                "list": "GET /api/user/keys",
                "create": "POST /api/user/keys"
            },
            "user": {
                "info": "GET /api/user/info"
            }
        }
    })


# ============================================================================
# Error Handlers (Hata İşleyiciler)
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🚀 Borç Takip API Server Başlatılıyor...")
    print("="*60)
    print("\n📍 Server: http://localhost:5000")
    print("📍 Android Emulator için: http://10.0.2.2:5000")
    print("\n💡 API Endpoints:")
    print("   GET  /health - Sağlık kontrolü")
    print("   GET  /api/transactions - Tüm işlemler")
    print("   POST /api/transactions - Yeni işlem")
    print("   GET  /api/user/info - Kullanıcı bilgisi")
    print("   GET  /api/user/keys - API anahtarları")
    print("\n🔑 Örnek API anahtarı oluşturmak için:")
    print("   python3 -c \"from api_key_manager import create_api_key; k, i = create_api_key('user123', 'Android'); print(f'API Key: {k}')\"")
    print("\n⚠️  Debug Mode: {}".format("Enabled" if DEBUG_MODE else "Disabled"))
    print("   Production'da debug=False kullanın!")
    print("\n" + "="*60 + "\n")
    
    # Server'ı başlat
    app.run(
        host='0.0.0.0',  # Tüm network interface'lerinden erişilebilir
        port=5000,
        debug=DEBUG_MODE  # Environment variable ile kontrol edilir
    )
