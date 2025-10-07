from flask import Flask, jsonify
import requests
from stem import Signal
from stem.control import Controller
import time
import json
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

class TorScraper:
    def __init__(self):
        self.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        # MongoDB bağlantısı
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['sofascore']
        self.matches_collection = self.db['matches']
    
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
        """MongoDB'den cache'lenmiş veriyi kontrol et"""
        try:
            # 1 dakikadan yeni veri var mı kontrol et
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            
            cached_data = self.matches_collection.find_one({
                'date': date,
                'created_at': {'$gte': one_minute_ago}
            })
            
            if cached_data:
                print(f"✅ Cache'den veri bulundu: {date}")
                return cached_data['data']
            else:
                print(f"❌ Cache'de veri yok veya eski: {date}")
                return None
        except Exception as e:
            print(f"❌ Cache kontrol hatası: {e}")
            return None
    
    def save_to_cache(self, date, data):
        """Veriyi MongoDB'ye kaydet"""
        try:
            # Eski veriyi sil
            self.matches_collection.delete_many({'date': date})
            
            # Yeni veriyi kaydet
            document = {
                'date': date,
                'data': data,
                'created_at': datetime.now(),
                'ip_used': data.get('ip_used', 'Unknown')
            }
            
            result = self.matches_collection.insert_one(document)
            print(f"✅ Veri MongoDB'ye kaydedildi: {date} - ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"❌ MongoDB kaydetme hatası: {e}")
            return False
    
    def scrape_sofascore(self, date='2025-10-07'):
        # Önce cache'den kontrol et
        cached_data = self.get_cached_data(date)
        if cached_data:
            return cached_data
        
        print(f"🔄 Yeni veri çekiliyor: {date}")
        self.change_ip()  # Yeni IP al
        time.sleep(10)  # Tor bootstrap için bekle
        
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
                
                # MongoDB'ye kaydet
                self.save_to_cache(date, data)
                
                return data
            else:
                error_data = {
                    'error': f'HTTP {response.status_code}',
                    'ip_used': self.get_current_ip()
                }
                self.save_to_cache(date, error_data)
                return error_data
        except Exception as e:
            error_data = {
                'error': str(e),
                'ip_used': self.get_current_ip()
            }
            self.save_to_cache(date, error_data)
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
