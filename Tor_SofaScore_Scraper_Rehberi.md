# Tor ile SofaScore API Scraper - Detaylı Rehber

## 📋 Proje Özeti

Bu proje, Tor Network kullanarak SofaScore API'sinden veri çeken ve her istekte farklı IP adresi kullanan bir web scraper sistemidir. Render.com üzerinde ücretsiz olarak deploy edilmiştir.

## 🎯 Proje Amacı

- SofaScore API'sine erişim
- Her istekte farklı IP adresi kullanma
- Bot detection'ı bypass etme
- Ücretsiz cloud platformunda çalıştırma

## 🛠️ Teknolojiler

- **Python 3.9**
- **Flask** (Web Framework)
- **Tor Network** (IP Rotation)
- **Requests** (HTTP Client)
- **Stem** (Tor Control)
- **Docker** (Containerization)
- **Render.com** (Cloud Platform)

## 📁 Proje Dosyaları

### 1. Dockerfile
```dockerfile
FROM python:3.9-slim

# Tor kurulumu
RUN apt-get update && apt-get install -y tor

# Tor konfigürasyonu
RUN echo "SocksPort 9050" > /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 0" >> /etc/tor/torrc

# Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Uygulama
COPY app.py /app/app.py

EXPOSE 8000

# Tor'u başlat ve uygulamayı çalıştır
CMD ["sh", "-c", "tor & sleep 5 && python /app/app.py"]
```

### 2. requirements.txt
```
requests[socks]==2.32.5
stem==1.8.2
flask==2.3.3
```

### 3. app.py (Ana Uygulama)
```python
from flask import Flask, jsonify
import requests
from stem import Signal
from stem.control import Controller
import time
import json

app = Flask(__name__)

class TorScraper:
    def __init__(self):
        self.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
    
    def get_current_ip(self):
        try:
            response = requests.get('https://api.ipify.org?format=json', proxies=self.proxies, timeout=10)
            return response.json()['ip']
        except:
            return 'Hata'
    
    def change_ip(self):
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                time.sleep(3)
                return True
        except:
            return False
    
    def scrape_sofascore(self):
        self.change_ip()  # Yeni IP al
        time.sleep(10)  # Tor bootstrap için bekle
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.sofascore.com/tr/',
            'Origin': 'https://www.sofascore.com'
        }
        
        url = 'https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07'
        
        try:
            response = requests.get(url, headers=headers, proxies=self.proxies, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data,
                    'ip_used': self.get_current_ip(),
                    'events_count': len(data.get('events', [])),
                    'message': 'SofaScore verisi başarıyla alındı'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'ip_used': self.get_current_ip(),
                    'message': 'SofaScore verisi alınamadı'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ip_used': self.get_current_ip(),
                'message': 'Bağlantı hatası'
            }

scraper = TorScraper()

@app.route('/')
def home():
    return jsonify({
        'message': 'Tor SofaScore Scraper API',
        'endpoints': {
            '/api/sofascore': 'SofaScore verilerini çek',
            '/api/ip': 'Mevcut IP adresini öğren'
        }
    })

@app.route('/api/sofascore')
def get_sofascore():
    result = scraper.scrape_sofascore()
    return jsonify(result)

@app.route('/api/ip')
def get_ip():
    ip = scraper.get_current_ip()
    return jsonify({
        'ip': ip,
        'message': 'Mevcut Tor IP adresi'
    })

if __name__ == '__main__':
    print('🌐 Tor SofaScore Scraper başlatılıyor...')
    print('⏳ Tor bağlantısı kuruluyor...')
    time.sleep(5)  # Tor'un başlaması için bekle
    print('🚀 API hazır!')
    app.run(host='0.0.0.0', port=8000, debug=False)
```

## 🚀 Kurulum Adımları

### 1. Local Geliştirme Ortamı

#### Tor Kurulumu (macOS)
```bash
# Homebrew ile Tor Browser
brew install --cask tor-browser

# Tor Service
brew install tor
brew services start tor
```

#### Python Dependencies
```bash
# Virtual environment oluştur
python3 -m venv tor-env
source tor-env/bin/activate

# Dependencies yükle
pip install requests[socks] stem flask
```

### 2. GitHub Repository Oluşturma

```bash
# Git repository başlat
git init
git add .
git commit -m "Initial commit"

# GitHub'a push
git remote add origin https://github.com/kullaniciadi/repository.git
git push -u origin main
```

### 3. Render.com Deploy

1. **Render.com**'a giriş yapın
2. **"New Project"** → **"Web Service"** seçin
3. **GitHub repository**'nizi bağlayın
4. **Deploy ayarları**:
   - **Name**: `tor-scraper`
   - **Runtime**: `Docker`
   - **Build Command**: (boş bırak)
   - **Start Command**: (boş bırak)
5. **"Create Web Service"** tıklayın

## 🔧 Tor Network Açıklaması

### Tor Nasıl Çalışır?

1. **Onion Routing**: Veri paketleri katmanlı şifreleme ile yönlendirilir
2. **Exit Nodes**: Farklı IP adreslerinden çıkış yapar
3. **Control Port**: IP değişimi için kontrol sağlar

### Proxy Ayarları
```python
proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}
```

### IP Değiştirme
```python
def change_ip(self):
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)  # Yeni IP al
        time.sleep(3)  # Değişim için bekle
```

## 📊 API Endpoints

### 1. Ana Sayfa
```
GET https://deneme-5sez.onrender.com/
```

**Yanıt:**
```json
{
  "endpoints": {
    "/api/ip": "Mevcut IP adresini öğren",
    "/api/sofascore": "SofaScore verilerini çek"
  },
  "message": "Tor SofaScore Scraper API"
}
```

### 2. SofaScore API
```
GET https://deneme-5sez.onrender.com/api/sofascore
```

**Yanıt:**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "tournament": {
          "name": "UEFA Champions League, Women, League Phase"
        }
      }
    ]
  },
  "ip_used": "185.220.101.153",
  "events_count": 78,
  "message": "SofaScore verisi başarıyla alındı"
}
```

### 3. IP Kontrol
```
GET https://deneme-5sez.onrender.com/api/ip
```

**Yanıt:**
```json
{
  "ip": "185.220.101.153",
  "message": "Mevcut Tor IP adresi"
}
```

## 🧪 Test Sonuçları

### IP Değişim Testi

**Test 1:**
```json
{
  "ip_used": "185.220.101.153",
  "success": true
}
```

**Test 2 (10 saniye sonra):**
```json
{
  "ip_used": "192.42.116.218",
  "success": true
}
```

**Test 3 (10 saniye sonra):**
```json
{
  "ip_used": "37.228.129.5",
  "success": true
}
```

### Sonuç
✅ **Her istekte farklı IP adresi kullanılıyor**
✅ **SofaScore API'si başarıyla çalışıyor**
✅ **Bot detection bypass ediliyor**

## 🔍 Sorun Giderme

### 1. SOCKS Desteği Hatası
```
"error": "Missing dependencies for SOCKS support."
```

**Çözüm:**
```python
# requirements.txt
requests[socks]==2.32.5  # [socks] ekleyin
```

### 2. Timeout Hatası
```
"error": "Connection to www.sofascore.com timed out"
```

**Çözüm:**
```python
# Timeout süresini artırın
response = requests.get(url, timeout=60)

# Tor bootstrap için bekleme ekleyin
time.sleep(10)
```

### 3. Tor Bootstrap Hatası
```
"error": "We have no usable consensus"
```

**Çözüm:**
```python
# Tor'un başlaması için bekleme
time.sleep(5)
```

## 📈 Performans

### Avantajlar
- ✅ **Ücretsiz**: Render.com free tier
- ✅ **Otomatik IP değişimi**: Her istekte farklı IP
- ✅ **Bot detection bypass**: Tor network kullanımı
- ✅ **Ölçeklenebilir**: Docker container
- ✅ **7/24 çalışır**: Cloud platform

### Dezavantajlar
- ❌ **Yavaş**: Tor network gecikmesi (10-15 saniye)
- ❌ **Bazen bağlantı kopabilir**: Tor network istikrarsızlığı
- ❌ **IP öğrenme**: Bazen çalışmayabilir

## 🔒 Güvenlik

### Tor Network Güvenliği
- **Anonimlik**: Gerçek IP adresi gizli
- **Şifreleme**: Katmanlı şifreleme
- **Exit Nodes**: Farklı coğrafi konumlar

### API Güvenliği
- **Rate Limiting**: Tor network tarafından
- **Timeout**: 60 saniye maksimum
- **Error Handling**: Kapsamlı hata yönetimi

## 🚀 Geliştirme Önerileri

### 1. Performans İyileştirmeleri
- **Connection Pooling**: Tor bağlantılarını yeniden kullan
- **Caching**: Verileri geçici olarak sakla
- **Async Requests**: Asenkron istekler

### 2. Özellik Ekleme
- **Multiple APIs**: Farklı API'ler için endpoint'ler
- **Scheduling**: Otomatik veri çekme
- **Database**: Verileri saklama

### 3. Monitoring
- **Health Check**: API durumu kontrolü
- **Logging**: Detaylı log kayıtları
- **Metrics**: Performans metrikleri

## 📚 Kaynaklar

### Dokümantasyon
- [Tor Project](https://www.torproject.org/)
- [Stem Library](https://stem.torproject.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Render.com Docs](https://render.com/docs)

### Kod Repository
- **GitHub**: `https://github.com/hakangzlyrt/deneme`
- **Live URL**: `https://deneme-5sez.onrender.com`

## 🎯 Sonuç

Bu proje, Tor Network kullanarak SofaScore API'sinden veri çeken ve her istekte farklı IP adresi kullanan başarılı bir web scraper sistemidir. Render.com üzerinde ücretsiz olarak deploy edilmiş ve test edilmiştir.

### Başarı Kriterleri
- ✅ **API Çalışıyor**: SofaScore verileri alınıyor
- ✅ **IP Değişimi**: Her istekte farklı IP
- ✅ **Bot Detection Bypass**: Tor network kullanımı
- ✅ **Ücretsiz Deploy**: Render.com free tier
- ✅ **7/24 Çalışır**: Cloud platform

### Kullanım
```bash
# SofaScore verilerini çek
curl https://deneme-5sez.onrender.com/api/sofascore

# Mevcut IP'yi öğren
curl https://deneme-5sez.onrender.com/api/ip
```

---

**Proje Tarihi**: 7 Ekim 2025  
**Geliştirici**: Hakan Güzelyurt  
**Platform**: Render.com  
**Status**: ✅ Aktif ve Çalışıyor
