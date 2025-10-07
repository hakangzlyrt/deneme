import json
import requests
import random
import time

def lambda_handler(event, context):
    try:
        # Session oluştur - Cookie'leri takip etmek için
        session = requests.Session()
        
        # Sürekli değişen 6 haneli X-Requested-With değeri oluştur
        random_x_requested_with = str(random.randint(100000, 999999))
        
        # Önce ana sayfayı ziyaret et - Cookie'leri almak için
        main_page_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Ana sayfayı ziyaret et
        main_page_response = session.get('https://www.sofascore.com/tr/', headers=main_page_headers, timeout=10)
        
        # API isteği için header'ları ayarla
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.sofascore.com/tr/',
            'Origin': 'https://www.sofascore.com',
            'X-Requested-With': random_x_requested_with,
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive'
        }
        
        # SofaScore API'sinden veri çek
        url = "https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07"
        
        # API isteği gönder - Session ile (cookie'ler otomatik gönderilir)
        response = session.get(url, headers=api_headers, timeout=10)
        
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
                    'x_requested_with_used': random_x_requested_with,
                    'main_page_status': main_page_response.status_code,
                    'cookies_received': len(session.cookies)
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
                    'message': 'SofaScore verisi alınamadı',
                    'response_text': response.text[:500],
                    'x_requested_with_used': random_x_requested_with
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
