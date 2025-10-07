// api/sofascore.js - Vercel Edge Function
export const config = {
  runtime: 'edge',
}

export default async function handler(req) {
  try {
    // SofaScore API'sinden veri çek
    const url = "https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07"
    
    // Sürekli değişen 6 haneli X-Requested-With değeri
    const randomXRequestedWith = Math.floor(Math.random() * 900000) + 100000
    
    // Header'ları ayarla
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
      'Accept': '*/*',
      'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
      'Referer': 'https://www.sofascore.com/tr/',
      'Origin': 'https://www.sofascore.com',
      'X-Requested-With': randomXRequestedWith.toString(),
      'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
      'Sec-Ch-Ua-Mobile': '?0',
      'Sec-Ch-Ua-Platform': '"Windows"',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive'
    }
    
    // API isteği gönder
    const response = await fetch(url, {
      method: 'GET',
      headers: headers
    })
    
    // HTTP durum kodunu kontrol et
    if (response.ok) {
      const data = await response.json()
      
      return new Response(JSON.stringify({
        success: true,
        data: data,
        message: 'SofaScore verisi başarıyla alındı',
        x_requested_with_used: randomXRequestedWith,
        status_code: response.status
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      })
    } else {
      const errorText = await response.text()
      
      return new Response(JSON.stringify({
        success: false,
        error: `API hatası: ${response.status}`,
        message: 'SofaScore verisi alınamadı',
        response_text: errorText.substring(0, 500),
        x_requested_with_used: randomXRequestedWith
      }), {
        status: response.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      })
    }
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
      message: 'Beklenmeyen hata oluştu'
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    })
  }
}
