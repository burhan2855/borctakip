# Android Studio'da API Anahtar Sistemi Nasıl Kullanılır?

Bu rehber, Python API anahtar sistemini Android uygulamanızla nasıl entegre edeceğinizi gösterir.

## 🏗️ Mimari Genel Bakış

```
┌─────────────────────────────────────────────────────────────┐
│                    Android Uygulamanız                       │
│  (Kotlin/Java - Borç Takip Uygulaması)                     │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP İstekleri
                   │ Authorization: Bearer sk_live_...
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend Server (Python/Flask)                   │
│  • api_auth_middleware.py - İstekleri doğrular             │
│  • api_key_manager.py - Anahtarları yönetir                │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Önkoşullar

1. **Backend Server Çalıştırın**: Python API sunucusu çalışıyor olmalı
2. **API Anahtarı Oluşturun**: Kullanıcı için bir API anahtarı oluşturulmuş olmalı

## 🚀 Adım 1: Backend Server Oluşturma

### 1.1. Flask Server Oluşturun

`server.py` dosyası oluşturun:

```python
from flask import Flask, request, jsonify
from api_auth_middleware import authenticate_api_request
import sqlite3

app = Flask(__name__)

def require_auth(f):
    """Authentication decorator"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_context = authenticate_api_request(auth_header)
        
        if not auth_context:
            return jsonify({"error": "Unauthorized"}), 401
        
        return f(auth_context, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/transactions', methods=['GET'])
@require_auth
def get_transactions(auth_context):
    """Kullanıcının işlemlerini getir"""
    user_id = auth_context['user_id']
    
    conn = sqlite3.connect('debt_database')
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
    
    return jsonify({"transactions": transactions})

@app.route('/api/transactions', methods=['POST'])
@require_auth
def create_transaction(auth_context):
    """Yeni işlem oluştur"""
    user_id = auth_context['user_id']
    data = request.get_json()
    
    conn = sqlite3.connect('debt_database')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions (userId, title, amount, isDebt, status, category, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, data['title'], data['amount'], data['isDebt'], 
          data['status'], data['category'], data['date']))
    
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"id": transaction_id, "message": "Created"}), 201

@app.route('/api/user/keys', methods=['GET'])
@require_auth
def get_user_keys(auth_context):
    """Kullanıcının API anahtarlarını listele"""
    from api_key_manager import list_user_api_keys
    
    user_id = auth_context['user_id']
    keys = list_user_api_keys(user_id)
    
    return jsonify({"keys": keys})

@app.route('/api/user/keys', methods=['POST'])
@require_auth
def create_user_key(auth_context):
    """Yeni API anahtarı oluştur"""
    from api_key_manager import create_api_key
    
    user_id = auth_context['user_id']
    data = request.get_json()
    key_name = data.get('key_name', 'Android App')
    
    api_key, key_info = create_api_key(user_id, key_name)
    
    if api_key:
        return jsonify({
            "api_key": api_key,
            "key_info": key_info
        }), 201
    else:
        return jsonify({"error": "Could not create key"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 1.2. Server'ı Çalıştırın

```bash
python3 server.py
```

Server `http://localhost:5000` adresinde çalışacak.

## 📱 Adım 2: Android Uygulamasını Yapılandırma

### 2.1. Gerekli İzinleri Ekleyin

`app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <!-- İnternet izni -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:usesCleartextTraffic="true">  <!-- Sadece geliştirme için -->
        ...
    </application>
</manifest>
```

### 2.2. Retrofit Kütüphanesini Ekleyin

`app/build.gradle` dosyasına:

```gradle
dependencies {
    // Retrofit - HTTP Client
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // OkHttp - Interceptor için
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
    
    // Coroutines - Asenkron işlemler için
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3'
    
    // ViewModel
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.2'
}
```

## 🔐 Adım 3: API Anahtarını Güvenli Şekilde Saklama

### 3.1. SharedPreferences ile Güvenli Saklama

`app/src/main/java/com/example/borctakip/data/ApiKeyManager.kt`:

```kotlin
package com.example.borctakip.data

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class ApiKeyManager(context: Context) {
    
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "api_key_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    companion object {
        private const val KEY_API_KEY = "api_key"
        private const val KEY_USER_ID = "user_id"
    }
    
    fun saveApiKey(apiKey: String, userId: String) {
        sharedPreferences.edit().apply {
            putString(KEY_API_KEY, apiKey)
            putString(KEY_USER_ID, userId)
            apply()
        }
    }
    
    fun getApiKey(): String? {
        return sharedPreferences.getString(KEY_API_KEY, null)
    }
    
    fun getUserId(): String? {
        return sharedPreferences.getString(KEY_USER_ID, null)
    }
    
    fun clearApiKey() {
        sharedPreferences.edit().clear().apply()
    }
    
    fun hasApiKey(): Boolean {
        return getApiKey() != null
    }
}
```

**Gradle'a ekleyin:**

```gradle
dependencies {
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'
}
```

## 🌐 Adım 4: API Client Oluşturma

### 4.1. API Response Modelleri

`app/src/main/java/com/example/borctakip/data/models/Models.kt`:

```kotlin
package com.example.borctakip.data.models

data class Transaction(
    val id: Int,
    val title: String,
    val amount: Double,
    val isDebt: Boolean,
    val status: String,
    val category: String,
    val date: String
)

data class TransactionResponse(
    val transactions: List<Transaction>
)

data class CreateTransactionRequest(
    val title: String,
    val amount: Double,
    val isDebt: Boolean,
    val status: String,
    val category: String,
    val date: String
)

data class CreateTransactionResponse(
    val id: Int,
    val message: String
)

data class ApiKeyResponse(
    val api_key: String,
    val key_info: KeyInfo
)

data class KeyInfo(
    val id: Int,
    val user_id: String,
    val key_name: String,
    val key_prefix: String,
    val created_at: String
)
```

### 4.2. API Service Interface

`app/src/main/java/com/example/borctakip/data/api/ApiService.kt`:

```kotlin
package com.example.borctakip.data.api

import com.example.borctakip.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    @GET("api/transactions")
    suspend fun getTransactions(): Response<TransactionResponse>
    
    @POST("api/transactions")
    suspend fun createTransaction(
        @Body request: CreateTransactionRequest
    ): Response<CreateTransactionResponse>
    
    @GET("api/user/keys")
    suspend fun getUserKeys(): Response<Map<String, Any>>
    
    @POST("api/user/keys")
    suspend fun createApiKey(
        @Body request: Map<String, String>
    ): Response<ApiKeyResponse>
}
```

### 4.3. Retrofit Client

`app/src/main/java/com/example/borctakip/data/api/RetrofitClient.kt`:

```kotlin
package com.example.borctakip.data.api

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    
    private const val BASE_URL = "http://10.0.2.2:5000/"  // Android emulator için
    // Gerçek cihaz için: "http://YOUR_COMPUTER_IP:5000/"
    
    private var apiKey: String? = null
    
    fun setApiKey(key: String) {
        apiKey = key
    }
    
    private val authInterceptor = Interceptor { chain ->
        val requestBuilder = chain.request().newBuilder()
        
        // API anahtarını Authorization header'a ekle
        apiKey?.let {
            requestBuilder.addHeader("Authorization", "Bearer $it")
        }
        
        chain.proceed(requestBuilder.build())
    }
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

## 🎯 Adım 5: Repository ve ViewModel

### 5.1. Repository

`app/src/main/java/com/example/borctakip/data/repository/TransactionRepository.kt`:

```kotlin
package com.example.borctakip.data.repository

import com.example.borctakip.data.api.RetrofitClient
import com.example.borctakip.data.models.CreateTransactionRequest
import com.example.borctakip.data.models.Transaction
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class TransactionRepository {
    
    private val apiService = RetrofitClient.apiService
    
    suspend fun getTransactions(): Result<List<Transaction>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getTransactions()
            if (response.isSuccessful) {
                Result.success(response.body()?.transactions ?: emptyList())
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createTransaction(
        title: String,
        amount: Double,
        isDebt: Boolean,
        status: String,
        category: String,
        date: String
    ): Result<Int> = withContext(Dispatchers.IO) {
        try {
            val request = CreateTransactionRequest(
                title, amount, isDebt, status, category, date
            )
            val response = apiService.createTransaction(request)
            if (response.isSuccessful) {
                Result.success(response.body()?.id ?: -1)
            } else {
                Result.failure(Exception("Error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 5.2. ViewModel

`app/src/main/java/com/example/borctakip/ui/TransactionViewModel.kt`:

```kotlin
package com.example.borctakip.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.borctakip.data.models.Transaction
import com.example.borctakip.data.repository.TransactionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class TransactionViewModel : ViewModel() {
    
    private val repository = TransactionRepository()
    
    private val _transactions = MutableStateFlow<List<Transaction>>(emptyList())
    val transactions: StateFlow<List<Transaction>> = _transactions
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error
    
    fun loadTransactions() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            repository.getTransactions()
                .onSuccess { transactions ->
                    _transactions.value = transactions
                }
                .onFailure { exception ->
                    _error.value = exception.message
                }
            
            _isLoading.value = false
        }
    }
    
    fun createTransaction(
        title: String,
        amount: Double,
        isDebt: Boolean,
        status: String,
        category: String,
        date: String
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            
            repository.createTransaction(title, amount, isDebt, status, category, date)
                .onSuccess {
                    loadTransactions()  // Listeyi yenile
                }
                .onFailure { exception ->
                    _error.value = exception.message
                }
            
            _isLoading.value = false
        }
    }
}
```

## 📲 Adım 6: Activity/Fragment'ta Kullanım

### 6.1. Login Activity

`app/src/main/java/com/example/borctakip/ui/LoginActivity.kt`:

```kotlin
package com.example.borctakip.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.borctakip.data.ApiKeyManager
import com.example.borctakip.data.api.RetrofitClient
import com.example.borctakip.databinding.ActivityLoginBinding

class LoginActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private lateinit var apiKeyManager: ApiKeyManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        apiKeyManager = ApiKeyManager(this)
        
        // Zaten API anahtarı varsa direkt ana ekrana git
        if (apiKeyManager.hasApiKey()) {
            val apiKey = apiKeyManager.getApiKey()!!
            RetrofitClient.setApiKey(apiKey)
            navigateToMainActivity()
            return
        }
        
        binding.btnLogin.setOnClickListener {
            val apiKey = binding.etApiKey.text.toString().trim()
            
            if (apiKey.isEmpty()) {
                Toast.makeText(this, "Lütfen API anahtarı girin", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            if (!apiKey.startsWith("sk_live_") && !apiKey.startsWith("sk_test_")) {
                Toast.makeText(this, "Geçersiz API anahtarı formatı", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            // API anahtarını kaydet
            apiKeyManager.saveApiKey(apiKey, "user_id")  // user_id'yi gerçek değerle değiştirin
            RetrofitClient.setApiKey(apiKey)
            
            Toast.makeText(this, "Giriş başarılı!", Toast.LENGTH_SHORT).show()
            navigateToMainActivity()
        }
    }
    
    private fun navigateToMainActivity() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
```

### 6.2. Main Activity

`app/src/main/java/com/example/borctakip/ui/MainActivity.kt`:

```kotlin
package com.example.borctakip.ui

import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.borctakip.data.ApiKeyManager
import com.example.borctakip.data.api.RetrofitClient
import com.example.borctakip.databinding.ActivityMainBinding
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var apiKeyManager: ApiKeyManager
    private val viewModel: TransactionViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        apiKeyManager = ApiKeyManager(this)
        
        // API anahtarını ayarla
        apiKeyManager.getApiKey()?.let { apiKey ->
            RetrofitClient.setApiKey(apiKey)
        }
        
        setupRecyclerView()
        observeViewModel()
        
        // İşlemleri yükle
        viewModel.loadTransactions()
        
        binding.btnRefresh.setOnClickListener {
            viewModel.loadTransactions()
        }
    }
    
    private fun setupRecyclerView() {
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        // Adapter'ı ayarlayın
    }
    
    private fun observeViewModel() {
        lifecycleScope.launch {
            viewModel.transactions.collect { transactions ->
                // RecyclerView'i güncelleyin
                Toast.makeText(
                    this@MainActivity,
                    "${transactions.size} işlem yüklendi",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
        
        lifecycleScope.launch {
            viewModel.isLoading.collect { isLoading ->
                // Loading indicator göster/gizle
                binding.progressBar.visibility = if (isLoading) {
                    android.view.View.VISIBLE
                } else {
                    android.view.View.GONE
                }
            }
        }
        
        lifecycleScope.launch {
            viewModel.error.collect { error ->
                error?.let {
                    Toast.makeText(this@MainActivity, "Hata: $it", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
```

## 🧪 Adım 7: Test Etme

### 7.1. API Anahtarı Oluşturma (Python)

```bash
cd /path/to/borctakip
python3 -c "
from api_key_manager import create_api_key
api_key, info = create_api_key('android_user_123', 'Android App')
print(f'API Anahtarı: {api_key}')
print('Bu anahtarı Android uygulamanızda kullanın!')
"
```

### 7.2. Server'ı Başlatma

```bash
python3 server.py
```

### 7.3. Android Uygulamayı Çalıştırma

1. Android Studio'da projeyi açın
2. Emulator veya gerçek cihazda çalıştırın
3. Login ekranında API anahtarını girin
4. İşlemleri görüntüleyin

## 🔧 Sorun Giderme

### "Connection refused" Hatası

Emulator kullanıyorsanız:
- `http://10.0.2.2:5000` kullanın (localhost yerine)

Gerçek cihaz kullanıyorsanız:
- Bilgisayarınızın IP adresini kullanın: `http://192.168.1.X:5000`
- Bilgisayar ve telefon aynı WiFi ağında olmalı

### "Unauthorized" Hatası

- API anahtarının doğru kopyalandığından emin olun
- API anahtarının iptal edilmediğinden emin olun
- Server loglarını kontrol edin

### "Cleartext HTTP traffic not permitted"

`AndroidManifest.xml` içinde:
```xml
<application
    android:usesCleartextTraffic="true">
```

Production için HTTPS kullanın!

## 📝 Özet

1. ✅ Python Flask server'ı çalıştırın
2. ✅ API anahtarı oluşturun
3. ✅ Android uygulamasına Retrofit ekleyin
4. ✅ API anahtarını güvenli şekilde saklayın
5. ✅ Her istekte Authorization header ekleyin
6. ✅ ViewModel ile verileri yönetin

## 🎓 Daha Fazla Bilgi

- [Retrofit Documentation](https://square.github.io/retrofit/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
