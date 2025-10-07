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
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Referer': 'https://www.sofascore.com/tr/',
            'Origin': 'https://www.sofascore.com',
            'Cookie': 'locale=tr; lang=tr; country=TR',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        url = 'https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07?locale=tr'
        
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
                # Raw JSON'u döndür, sadece IP bilgisini ekle
                data['ip_used'] = self.get_current_ip()
                return data
            else:
                return {
                    'error': f'HTTP {response.status_code}',
                    'ip_used': self.get_current_ip()
                }
        except Exception as e:
            return {
                'error': str(e),
                'ip_used': self.get_current_ip()
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
