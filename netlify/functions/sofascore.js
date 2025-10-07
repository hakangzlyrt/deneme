// netlify/functions/sofascore.js
exports.handler = async (event, context) => {
  try {
    const url = "https://www.sofascore.com/api/v1/sport/football/scheduled-events/2025-10-07"
    const randomXRequestedWith = Math.floor(Math.random() * 900000) + 100000
    
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
      'Sec-Fetch-Site': 'same-origin'
    }
    
    const response = await fetch(url, { headers })
    
    if (response.ok) {
      const data = await response.json()
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          success: true,
          data: data,
          message: 'SofaScore verisi başarıyla alındı',
          x_requested_with_used: randomXRequestedWith
        })
      }
    } else {
      const errorText = await response.text()
      return {
        statusCode: response.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          success: false,
          error: `API hatası: ${response.status}`,
          message: 'SofaScore verisi alınamadı',
          response_text: errorText.substring(0, 500),
          x_requested_with_used: randomXRequestedWith
        })
      }
    }
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        success: false,
        error: error.message,
        message: 'Beklenmeyen hata oluştu'
      })
    }
  }
}
