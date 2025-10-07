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
        # Basit cache sistemi (memory-based)
        self.cache = {}
        self.cache_timestamps = {}
    
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
    
    def get_cached_data(self, date):
        """Memory cache'den veriyi kontrol et"""
        try:
            # 1 dakikadan yeni veri var mı kontrol et
            if date in self.cache:
                cache_time = self.cache_timestamps[date]
                if time.time() - cache_time < 60:  # 1 dakika
                    print(f"✅ Cache'den veri bulundu: {date}")
                    return self.cache[date]
                else:
                    # Eski veriyi sil
                    del self.cache[date]
                    del self.cache_timestamps[date]
            
            print(f"❌ Cache'de veri yok veya eski: {date}")
            return None
        except Exception as e:
            print(f"❌ Cache kontrol hatası: {e}")
            return None
    
    def save_to_cache(self, date, data):
        """Veriyi memory cache'e kaydet"""
        try:
            # Memory cache'e kaydet
            self.cache[date] = data
            self.cache_timestamps[date] = time.time()
            print(f"✅ Veri cache'e kaydedildi: {date}")
            return True
        except Exception as e:
            print(f"❌ Cache kaydetme hatası: {e}")
            return False
    
    def scrape_sofascore(self, date='2025-10-07'):
        # Önce cache'den kontrol et
        cached_data = self.get_cached_data(date)
        if cached_data:
            return cached_data
        
        print(f"🔄 Yeni veri çekiliyor: {date}")
        
        # IP değiştirme ve veri çekme döngüsü - VERİ GELENE KADAR
        attempt = 0
        while True:
            attempt += 1
            print(f"🔄 Deneme {attempt} - Veri gelene kadar devam...")
            
            # IP değiştir
            self.change_ip()
            time.sleep(10)  # Tor bootstrap için bekle
            
            # Veri çekmeyi dene
            result = self._fetch_sofascore_data(date)
            
            # Başarılı ise döndür
            if result.get('events') or (not result.get('error')):
                print(f"✅ Veri başarıyla alındı! Deneme: {attempt}")
                return result
            
            # 403 hatası varsa tekrar dene
            if result.get('error') and ('403' in str(result.get('error')) or 'Forbidden' in str(result.get('error'))):
                print(f"❌ 403 Forbidden - IP değiştiriliyor... (Deneme: {attempt})")
                continue
            
            # Başka hatalar için de tekrar dene (network, timeout vs.)
            if result.get('error'):
                print(f"❌ Hata: {result.get('error')} - IP değiştiriliyor... (Deneme: {attempt})")
                continue
            
            # Beklenmeyen durum
            print(f"⚠️ Beklenmeyen durum - Tekrar deneniyor... (Deneme: {attempt})")
            continue
    
    def _fetch_sofascore_data(self, date):
        """SofaScore'dan veri çekme fonksiyonu"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Referer': 'https://www.sofascore.com/tr/',
            'Origin': 'https://www.sofascore.com',
            'Cookie': 'locale=tr; lang=tr; country=TR',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        url = f'https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date}'
        
        # Session kullan, önce ana sayfayı ziyaret et
        session = requests.Session()
        session.proxies.update(self.proxies)
        
        try:
            # Önce ana sayfayı ziyaret et
            session.get('https://www.sofascore.com/tr/', headers=headers, timeout=30)
            time.sleep(2)
            
            # Sonra API'yi çağır
            response = session.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                # IP bilgisini ekle
                data['ip_used'] = self.get_current_ip()
                
                # Cache'e kaydet
                self.save_to_cache(date, data)
                
                return data
            else:
                error_data = {
                    'error': f'HTTP {response.status_code}',
                    'ip_used': self.get_current_ip()
                }
                # 403 hatası cache'e kaydetme
                if response.status_code != 403:
                    self.save_to_cache(date, error_data)
                return error_data
        except Exception as e:
            error_data = {
                'error': str(e),
                'ip_used': self.get_current_ip()
            }
            return error_data

scraper = TorScraper()

@app.route('/')
def home():
    return jsonify({
        'message': 'Tor SofaScore Scraper API',
        'endpoints': {
            '/api/scorelive/matches/<date>': 'ScoreLive maç verilerini çek',
            '/api/ip': 'Mevcut IP adresini öğren'
        }
    })

@app.route('/api/scorelive/matches/<date>')
def get_scorelive_matches(date):
    result = scraper.scrape_sofascore(date)
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
