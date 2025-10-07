# SofaScore Edge Function

Bu proje SofaScore API'sine erişim için Vercel Edge Function kullanır.

## 🚀 Kurulum

1. **Vercel CLI yükleyin**:
```bash
npm i -g vercel
```

2. **Projeyi deploy edin**:
```bash
vercel
```

3. **Production'a deploy edin**:
```bash
vercel --prod
```

## 📁 Dosya Yapısı

```
├── api/
│   └── sofascore.js    # Edge Function
├── package.json        # Proje konfigürasyonu
└── README.md          # Bu dosya
```

## 🔧 Özellikler

- ✅ Edge Runtime kullanır
- ✅ Sürekli değişen X-Requested-With değeri
- ✅ CORS desteği
- ✅ Hata yönetimi
- ✅ Farklı IP'lerden istek

## 🌐 Kullanım

Deploy ettikten sonra:
```
https://your-project.vercel.app/api/sofascore
```

## 🎯 Avantajlar

- **Edge Network**: Global CDN'den farklı IP'ler
- **Hızlı**: Edge lokasyonlarından yakın sunucular
- **Ücretsiz**: Vercel'in ücretsiz planı
- **Kolay**: Tek komutla deploy
# SofaScore Edge Function - Build Fix
