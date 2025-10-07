import json
import requests
import random
import time

def lambda_handler(event, context):
    try:
        # SofaScore API'sinden veri çek
        url = "https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07"
        
        # Sürekli değişen 6 haneli X-Requested-With değeri oluştur
        random_x_requested_with = str(random.randint(100000, 999999))
        
        # Header'ları ayarla - X-Requested-With sürekli değişiyor!
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.sofascore.com/tr/',
            'Origin': 'https://www.sofascore.com',
            'X-Requested-With': random_x_requested_with,  # Her seferinde farklı 6 haneli sayı!
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        # API isteği gönder
        response = requests.get(url, headers=headers, timeout=10)
        
        # HTTP durum kodunu kontrol et
        if response.status_code == 200:
            # JSON verisini al
            data = response.json()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'data': data,
                    'message': 'SofaScore verisi başarıyla alındı',
                    'x_requested_with_used': random_x_requested_with
                })
            }
        else:
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': f'API hatası: {response.status_code}',
                    'message': 'SofaScore verisi alınamadı'
                })
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'SofaScore bağlantı hatası oluştu'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'SofaScore beklenmeyen hata oluştu'
            })
        }
