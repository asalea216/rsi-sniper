# 🚀 PAXG/USDT RSI Sniper Bot

PC kapalıyken bile çalışan, bulut tabanlı Telegram trading bot.

---

## ☁️ ÜCRETSİZ DEPLOY — Railway.app (Önerilen)

### 1. Adım — GitHub'a yükle
1. [github.com](https://github.com) → Yeni repo oluştur (private olabilir)
2. Bu 3 dosyayı yükle: `bot.py`, `requirements.txt`, `Procfile`

### 2. Adım — Railway'e bağla
1. [railway.app](https://railway.app) → GitHub ile giriş yap
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Repoyu seç → Otomatik deploy başlar!

### 3. Adım — Kontrol et
- Railway dashboard'da logları görebilirsin
- Bot başlayınca Telegram'a "Bot Başlatıldı" mesajı gelecek
- **Ücretsiz planda ayda ~500 saat** çalışır (yeterli!)

---

## 🔄 ALTERNATİF — Render.com

1. [render.com](https://render.com) → GitHub ile giriş
2. **"New"** → **"Background Worker"**
3. Repoyu bağla
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python bot.py`
6. **Deploy!**

---

## 🛠️ Geliştirmeler (Yapılanlar)

- ✅ **Otomatik yeniden bağlanma** — Ağ hatalarında tekrar dener
- ✅ **Log dosyası** — `bot.log` dosyasına kayıt tutar
- ✅ **Telegram HTML formatı** — Mesajlar daha okunaklı
- ✅ **Başlangıç bildirimi** — Bot açılınca Telegram'a mesaj atar
- ✅ **Kritik hata bildirimi** — 10 ardışık hata olursa uyarı gönderir
- ✅ **Rate limit koruması** — Binance API sınırlarına uyar

---

## ⚙️ Ayarlar (bot.py içinde)

```python
TOKEN = "..."       # Telegram bot token
CHAT_ID = "..."     # Telegram chat ID
SYMBOL = 'PAXG/USDT'
UPPER_RSI = 70
LOWER_RSI = 30
CHECK_INTERVAL = 10  # Kaç saniyede bir kontrol (saniye)
```
